from django.views.generic import TemplateView
from data.models import DataFrame

import MySQLdb
import warnings
import numpy as np
import scipy as sp
import sklearn as sk
import random

from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer


####################### View - Predictions #######################

class PredictionsView(TemplateView):
	template_name = "predictions.html"

	def get(self, request, *args, **kwargs):
		context = super(PredictionsView, self).get_context_data(**kwargs)
		
		dataframe_id = request.GET.get('dataframe_id')
		target_name = request.GET.get('target_name')
# 		training_nrow = int( request.GET.get('training_nrow') )
		training_percent = int(request.GET.get('training_percent'))
		column_exclusions = request.GET.get('column_exclusions').split(',')
		filter_clauses = request.GET.getlist('filter_clauses[]')

		query_where = "WHERE " + 'AND '.join(filter_clauses) if filter_clauses else ""
		
		try:
			df = DataFrame.objects.get(pk = dataframe_id)
		except Exception,e:
			context['debug'] = "No DataFrame Found"
			return self.render_to_response(context)

		columns = df.columns.keys()
		column_pk_name = 'id'
		target_role = df.columns[target_name]['role']

		column_names_with_prediction = [key for key in columns if "prediction" in key]
		drop_columns(df.get_db(), df.db_table_name, column_names_with_prediction)

		# Refresh column names after the prediction columns have been removed
		# Also remove any date type columns
		columns = [key for key in df.columns if "date" not in df.columns[key]['type']]
 		columns = list( set(columns) -  set(column_exclusions) )

		# Ensure column order starts like [id, target, feature1, feature2, ...]
		columns.remove(column_pk_name)
		columns.remove(target_name)
		columns.insert(0, column_pk_name)
		columns.insert(1, target_name)

#		tmpnp = mysql2numpy(df.get_db(), df.db_table_name, columns)

		query = "SELECT %s, %s FROM %s %s" % (column_pk_name, target_name, df.db_table_name, query_where);
		y_and_ids_as_dicts, column_names = df.query_results(query)
		y = [v[target_name] for v in y_and_ids_as_dicts]
		ids = [v[column_pk_name] for v in y_and_ids_as_dicts]

		query = "SELECT %s FROM %s %s" % (','.join(columns[2:]), df.db_table_name, query_where);
		# X_as_dicts, column_names = df.query_results(query)  (older way, doing in two steps instead)
		X_as_tuples, column_names = df.query_results(query, "tuples")
		print("finished retrieving as tuples");
		X_as_dicts = [dict(zip(column_names, x_tuple)) for x_tuple in X_as_tuples]
		print("finished converting to dicts");

		nrow = len(y)
		training_nrow = int(nrow * training_percent / 100)
		indexes = range(nrow)
		training_indexes = random.sample(range(nrow), training_nrow)
		test_indexes = list(set(indexes) - set(training_indexes))
		#test_indexes = [x for x in indexes if x not in training_indexes] < The old way was very inefficient
		
		vec = DictVectorizer()
		X = vec.fit_transform(X_as_dicts).toarray()
		# vec.get_feature_names()
		print("finished vectorizing");

		X_train = X[training_indexes, :]
		y_train = np.array(y)[training_indexes]

		X_test = X[test_indexes, :]
		y_test = np.array(y)[test_indexes]

		# Create an array of values that all say "Training" then replace the right rows with "Training"
		predictions_role = np.repeat("Training",len(X))
		predictions_role[test_indexes] = "Testing"

		if target_role == "dimension":
			print("starting fit classification model");
			clf = RandomForestClassifier(n_estimators=500, n_jobs = -1, verbose=1, bootstrap=False)
			clf = clf.fit(X_train, y_train)
			predictions = clf.predict(X)
			predictions_proba = clf.predict_proba(X)
			predictions_proba_classes = list(clf.classes_)
			predictions_confidence = np.sort(predictions_proba)[:,-1]
		elif target_role == "measure":
			print("starting fit regression model");
			clf = RandomForestRegressor(n_estimators=500, n_jobs = -1, verbose=1)
			clf = clf.fit(X_train, y_train)
			predictions = clf.predict(X)
			predictions_confidence = np.repeat(.5,len(X))

		print("finished fitting model")
		feature_importances = dict(zip(column_names, clf.feature_importances_))

		#score_train = clf.score(X_train, y_train)
		#score_test = clf.score(X_test, y_test)

		if target_role == "dimension":
			predictions_accurate = predictions == y
	
			predictions_array = np.column_stack((ids, predictions, predictions_confidence, predictions_accurate, predictions_role)) # not including predictions_proba for class probabilities
			predictions_array_column_names = ['id', 'prediction', 'prediction_confidence', 'prediction_accurate', 'prediction_role'] # + [i + "_probability" for i in predictions_proba_classes]
			predictions_array_types = ['int(11) NOT NULL PRIMARY KEY', 'varchar(255)', 'double', 'varchar(5)', 'varchar(8)'] # ['double'] * len(predictions_proba_classes)

			df.add_columns(predictions_array_column_names[1:], predictions_array_types[1:])
			predictions_array = np.column_stack((ids, predictions, predictions_confidence, predictions_accurate, predictions_role)) # not including predictions_proba for class probabilities
			predictions_array_column_names = ['id', 'prediction', 'prediction_confidence', 'prediction_accurate', 'prediction_role'] # + [i + "_probability" for i in predictions_proba_classes]

		elif target_role == "measure":
			prediction_accurate = predictions - y
			predictions_array = np.column_stack((ids, predictions, predictions_confidence, prediction_accurate, predictions_role))
			predictions_array_column_names = ['id', 'prediction', 'prediction_confidence', 'prediction_accurate', 'prediction_role']
			predictions_array_types = ['int(11) NOT NULL PRIMARY KEY', 'int(11)', 'double', 'int(11)', 'varchar(8)']

		df.add_columns(predictions_array_column_names[1:], predictions_array_types[1:])

		db_tmp_table_name = df.db_table_name + '_tmp'
		db_tmp_table_data = predictions_array[:,0:5]
		
		# Increase size for large writes
		df.query_results("set global net_buffer_length=1000000")
		df.query_results("set global max_allowed_packet=1000000000")


		drop_table(df.get_db(), db_tmp_table_name)
		create_table(df.get_db(), db_tmp_table_name, predictions_array_column_names, predictions_array_types)
		insert_table(df.get_db(), db_tmp_table_name, predictions_array_column_names, db_tmp_table_data.tolist())
		merge_tables(df.get_db(), df.db_table_name, db_tmp_table_name, 'id')
		drop_table(df.get_db(), db_tmp_table_name)
		print("finished database operations");
		
		
# 		context['debug'] = X_train
		return self.render_to_response(context)
		
####################### Functions - Predictions #######################

def mysql2numpy(db, table_name, columns):
	cursor = db.cursor()
	cursor.execute("SELECT %s FROM %s" % (",".join(columns), table_name))
	## Perhaps we should do something like this to avoid having the fetchall iterable stored in memory before conversion to numpy
	# df_dtypes = ()
	# for column_key in columns:
	# 	df_type = df.columns[column_key]['type']
	# 	if df_type == 'varchar':
	# 		df_type = 'S' + df.columns[column_key]['length']
	# 	elif df_type == 'int':
	# 		df_type = 'i'
	# 	elif df_type == 'double':
	# 		df_type = 'double'
	# 	elif df_type == 'date':
	# 		df_type = 'datetime64[D]'
	# 	df_dtypes = df_dtypes + (df_type,)
	#np_array = np.fromiter(cursor.fetchall(), dtype=",".join(df_dtypes))
	np_array = np.array(cursor.fetchall())
	return np_array

def create_table(db, table_name, column_names, column_types):
	cursor = db.cursor()
	column_definition_fragments = [column_names[i] + ' ' + column_types[i] for i, junk in enumerate(column_names)]
	column_definition = '(' + ','.join(column_definition_fragments) + ')'
	cursor.execute("CREATE TABLE %s %s" % (table_name, column_definition))
	cursor.close()

def drop_table(db, table_name):
	cursor = db.cursor()
	warnings.filterwarnings('ignore', 'Unknown table .*')
	cursor.execute("DROP TABLE IF EXISTS %s" % table_name)
	db.commit()
	cursor.close()

def insert_table(db, table_name, column_names, table_data):
	cursor = db.cursor()
	column_names_string = '(' + ','.join(column_names) + ')'
	column_placeholders_string = '(' + ','.join(['%s'] * len(column_names)) + ')'
	query = "INSERT INTO %s %s VALUES %s" % (table_name, column_names_string, column_placeholders_string)
	cursor.executemany(query , table_data)
	db.commit()
	cursor.close()

def merge_tables(db, table_a, table_b, join_column):
	cursor = db.cursor()
	query = "UPDATE %s a JOIN %s b ON a.%s = b.%s SET a.prediction = b.prediction, a.prediction_confidence = b.prediction_confidence, a.prediction_accurate = b.prediction_accurate, a.prediction_role = b.prediction_role" % (table_a, table_b, join_column, join_column)
	cursor.execute(query)
	db.commit()
	cursor.close()

def drop_columns(db, table_name, column_names):
	cursor = db.cursor()
	query = "ALTER TABLE %s %s" % (table_name, ','.join(['DROP ' + i for i in column_names]))
	cursor.execute(query)
	db.commit()
	cursor.close()


