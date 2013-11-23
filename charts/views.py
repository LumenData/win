from django.views.generic import TemplateView
from data.models import DataFrame
from django.http import HttpResponse
import json
from decimal import Decimal
import datetime

import pprint
import sys
from django.utils import timezone


####################### View - Chart Builder #######################

class ChartBuilderView(TemplateView):
	template_name = "chart_builder.html"

	def get(self, request, *args, **kwargs):
		context = super(ChartBuilderView, self).get_context_data(**kwargs)

		try:
			dataframe = DataFrame.objects.get(pk = request.GET.get('dataframe_id'))
		except Exception,e:
			context['no_dataframe'] = True
			context['object_list'] = DataFrame.objects.all()			
			return self.render_to_response(context)

		context['dataframe'] = dataframe
		return self.render_to_response(context)
		
####################### View - AutoChart #######################

class AutoChartView(TemplateView):
	template_name = "autochart.html"

	def get(self, request, *args, **kwargs):
		context = super(AutoChartView, self).get_context_data(**kwargs)

		# Get the state of the chart builder app "chart_builder_input"
		chart_builder_input = json.loads(request.GET.get("chart_builder_input"))
		dataframe_id = chart_builder_input["dataframe_id"]

		# Get the dataframe
		try:
			dataframe = DataFrame.objects.get(pk = dataframe_id)
		except Exception,e:
			context['debug'] = str(e)
			return self.render_to_response(context)

		chart_type = chart_selector(dataframe, chart_builder_input)
		query = query_builder(dataframe, chart_type, chart_builder_input)

		# Create chart data & chart options to pass to javascript
		if(chart_type == "none"):
			chart_data = []
			chart_options = {}
		elif(chart_type == "pieChart"):
			query_results, tmp = dataframe.query_results(query);	
			chart_data = list(query_results)
			chart_options = {}
		elif(chart_type in ("lineChart", "scatterChart", "barChart")):
			query_results, query_headings = dataframe.query_results(query)
			chart_data, chart_options = get_chart_data(dataframe, query_results, chart_builder_input)
		else:
			context['error_message'] = "That analysis type hasn't been implemented yet"

		context['chart_type'] = chart_type
		context['chart_data'] = json.dumps(chart_data, cls=CustomJSONEncoder)
		context['chart_options'] = json.dumps(chart_options)

		print("\n\nChart Data: ")
		pprint.pprint(chart_data)
		print("\n\nChart Query: ")
		pprint.pprint(query)
		print("\n\nChart Options: ")
		pprint.pprint(chart_options)
		
		return self.render_to_response(context)


####################### Chart Selector #######################

def chart_selector(dataframe, chart_builder_input):
	ncols = len(chart_builder_input["column_names"])
	nrows = len(chart_builder_input["row_names"])
	
	datacols = dataframe.columns;

	## Get xaxis and yaxis data types (note: assumes only one x and one y)

	col_datatype = datacols[chart_builder_input["column_names"][0]]["type_category"]	if(ncols > 0) else ""
	row_datatype = datacols[chart_builder_input["row_names"][0]]["type_category"] 	if(nrows > 0) else ""

	if (ncols + nrows) == 1:
		return "pieChart"  
	elif (ncols ==1) and (nrows == 1) and (col_datatype == "time") and (row_datatype == "numeric"):
		return "lineChart"
	elif (ncols ==1) and (nrows == 1) and (col_datatype == "character") and (row_datatype == "numeric"):
		return "barChart"
	elif (ncols == 1) and (nrows == 1) and (col_datatype == "numeric") and (row_datatype == "numeric"):
		return "scatterChart"  
	else:
		return "none"


####################### Query Builder #######################


def query_builder(dataframe, chart_type, chart_builder_input):
	
	column_names = chart_builder_input["column_names"]
	row_names = chart_builder_input["row_names"]
	group_names = chart_builder_input["group_names"]
	size_names = chart_builder_input["size_names"][0] if chart_builder_input["size_names"] else 1
	
	single_column_name = (row_names[:1] or column_names[:1])[0]
	
	if(chart_type == "pieChart"):
		query = "SELECT %s `key`, count(*) y FROM %s GROUP BY 1 ORDER BY 2 DESC LIMIT 100" % (single_column_name, dataframe.db_table_name)
	elif(chart_type == "lineChart"):		
		if(group_names):
			query = "SELECT %s x, avg(%s) y, %s g FROM %s GROUP BY 1, 3 ORDER BY 1" % (column_names[0], row_names[0], group_names[0], dataframe.db_table_name)
		else:
			query = "SELECT %s x, avg(%s) y FROM %s GROUP BY 1 ORDER BY 1" % (column_names[0], row_names[0], dataframe.db_table_name)
	elif(chart_type == "barChart"):
		if(group_names):
			query = "SELECT %s x, avg(%s) y, %s g FROM %s GROUP BY 1, 3 ORDER BY 2 DESC LIMIT 1000" % (column_names[0], row_names[0], group_names[0], dataframe.db_table_name )
		else:
			query = "SELECT %s label, avg(%s) value FROM %s GROUP BY 1 ORDER BY 2 DESC LIMIT 20" % (column_names[0], row_names[0], dataframe.db_table_name )
	elif(chart_type == "scatterChart"):
		if(group_names):
			query = "SELECT %s x, %s y, %s size, %s g FROM %s ORDER BY 4" % (column_names[0], row_names[0], size_names, group_names[0], dataframe.db_table_name)
		else:
			query = "SELECT %s x, %s y, %s size FROM %s" % (column_names[0], row_names[0], size_names, dataframe.db_table_name)
	else:
		query = "error"
		
	return query

####################### Generate Query & Chart Options #######################

def get_chart_data(dataframe, query_results, chart_builder_input):

	column_names = chart_builder_input["column_names"]
	row_names = chart_builder_input["row_names"]
	group_names = chart_builder_input["group_names"]
	size_names = chart_builder_input["size_names"][0] if chart_builder_input["size_names"] else None


	if(group_names == []):
		query_results_as_list = list(query_results)
		chart_data = [{"key": row_names[0], "values":  query_results_as_list}]	
	else:
		# Build a dictionary where each group value is a key for an array of x/y values		
		query_results_group_dict = {}
		
		# MYSQLdb returns each row as a dict of column-name/row-value pairs
		# Loop through each row of the query results
		for dict in query_results:
			# Build a array of dictionaries for each group (of x/y pairs for that group).  
			# Instantiate new array if none exist
			if(dict['g'] not in query_results_group_dict.keys()):
				query_results_group_dict[dict['g']] = []
				
			# Populate the array element with a new element, a dict of x/y or x/y/size pairs	
			if(size_names):
				query_results_group_dict[dict['g']].append({'x': dict['x'], 'y': dict['y'], 'size': dict['size']})
			else:
				query_results_group_dict[dict['g']].append({'x': dict['x'], 'y': dict['y']})
			
		# Instantiate a list then create an array where each element has all x/y/size data for a group value
		chart_data = []
		for key in query_results_group_dict.keys():
			one_group_data = {'key': key, 'values': query_results_group_dict[key]}
			chart_data.append(one_group_data)

	# 	Should pass function rather than using avg later
	chart_options = {
		"xaxis_label": column_names[0],
		"xaxis_type": dataframe.columns[column_names[0]]["type"],
		"yaxis_label": "avg(" + row_names[0] + ")",
		"size_label": size_names if size_names else "",
		"group_label": group_names[0] if group_names else ""
	}

	return chart_data, chart_options


####################### Custom JSON Encoder #######################

class CustomJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if hasattr(obj, 'isoformat'): #handles both date and datetime objects
			return obj.isoformat()
		elif isinstance(obj, datetime.timedelta):
			return str(obj)
		elif isinstance(obj, Decimal):
			return float(obj)
		else:
			return json.JSONEncoder.default(self, obj)
