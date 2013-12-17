from django.views.generic import TemplateView
from data.models import DataFrame

import MySQLdb
import numpy as np
import scipy as sp
import sklearn as sk
import random
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier


####################### View - Predictions #######################

class PredictionsView(TemplateView):
	template_name = "predictions.html"

	def get(self, request, *args, **kwargs):
		context = super(PredictionsView, self).get_context_data(**kwargs)
		
		dataframe_id = request.GET.get('dataframe_id')
		target_name = request.GET.get('target_name')
		training_nrow = int( request.GET.get('training_nrow') )
		
		try:
			df = DataFrame.objects.get(pk = dataframe_id)
		except Exception,e:
			context['debug'] = "No DataFrame Found"
			return self.render_to_response(context)

		columns = df.columns.keys()
		column_pk_name = 'id'

		column_names_with_prediction = [i for i in columns if "prediction" in i]
		drop_columns(df.get_db(), df.db_table_name, column_names_with_prediction)
		
		# Refresh column names after the prediction columns have been removed
		columns = df.columns.keys()
		
		# Ensure column order starts like [id, target, feature1, feature2, ...]
		columns.remove(column_pk_name)
		columns.remove(target_name)
		columns.insert(0, column_pk_name)
		columns.insert(1, target_name)

		np_array = mysql2numpy(df.get_db(), df.db_table_name, columns)

		nrow = len(np_array)
		indexes = range(nrow)
		training_indexes = random.sample(range(nrow), training_nrow)
		test_indexes = [x for x in indexes if x not in training_indexes]

		ids = np_array[:, 0]
		y = np_array[:, 1]
		X = np_array[:, 2:5]

		X_train = X[training_indexes, :]
		y_train = y[training_indexes]

		X_test = X[test_indexes, :]
		y_test = y[test_indexes]

		clf = RandomForestClassifier(n_estimators=1)
		clf = clf.fit(X_train, y_train)

		predictions = clf.predict(X)
		predictions_accurate = predictions == y
		predictions_proba = clf.predict_proba(X)
		predictions_proba_classes = list(clf.classes_)
		predictions_confidence = np.sort(predictions_proba)[:,-1]

# 		score_train = clf.score(X_train, y_train)
# 		score_test = clf.score(X_test, y_test)

		predictions_array = np.column_stack((ids, predictions, predictions_confidence, predictions_accurate, predictions_proba))
		predictions_array_column_names = ['id', 'prediction', 'prediction_confidence', 'prediction_accurate'] # + [i + "_probability" for i in predictions_proba_classes]
		predictions_array_types = ['int(11) NOT NULL PRIMARY KEY', 'varchar(255)', 'double', 'varchar(5)'] # ['double'] * len(predictions_proba_classes)

		df.add_columns(predictions_array_column_names[1:], predictions_array_types[1:])

		db_tmp_table_name = df.db_table_name + '_tmp'
		db_tmp_table_data = predictions_array[:,0:4]
		
		create_table(df.get_db(), db_tmp_table_name, predictions_array_column_names, predictions_array_types)
		insert_table(df.get_db(), db_tmp_table_name, predictions_array_column_names, db_tmp_table_data.tolist())
		merge_tables(df.get_db(), df.db_table_name, db_tmp_table_name, 'id')
		drop_table(df.get_db(), db_tmp_table_name)

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
	cursor.execute("DROP TABLE %s" % table_name)
	cursor.close()

def insert_table(db, table_name, column_names, table_data):
	cursor = db.cursor()
	column_names_string = '(' + ','.join(column_names) + ')'
	column_placeholders_string = '(' + ','.join(['%s'] * len(column_names)) + ')'
	query = "INSERT INTO %s %s VALUES %s" % (table_name, column_names_string, column_placeholders_string)
	cursor.executemany(query , table_data)
	cursor.close()

def merge_tables(db, table_a, table_b, join_column):
	cursor = db.cursor()
	query = "UPDATE %s a JOIN %s b ON a.%s = b.%s SET a.prediction = b.prediction, a.prediction_confidence = b.prediction_confidence, a.prediction_accurate = b.prediction_accurate" % (table_a, table_b, join_column, join_column)
	cursor.execute(query)
	cursor.close()

def drop_columns(db, table_name, column_names):
	cursor = db.cursor()
	query = "ALTER TABLE %s %s" % (table_name, ','.join(['DROP ' + i for i in column_names]))
	cursor.execute(query)
	cursor.close()

