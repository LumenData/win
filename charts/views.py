from django.views.generic import TemplateView
from data.models import DataFrame
from django.http import HttpResponse
import json
from decimal import Decimal
import datetime

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

		# Create chart data & chart options to pass to javascript
		if(chart_type == "none"):
			chart_data = []
			chart_options = {}
		elif(chart_type == "pieChart"):
			chart_data, chart_options = pie_chart(dataframe, chart_builder_input)
		elif(chart_type == "lineChart"):
			chart_data, chart_options = line_chart(dataframe, chart_builder_input)
		elif(chart_type == "scatterChart"):
			chart_data, chart_options = scatter_chart(dataframe, chart_builder_input)
		elif(chart_type == "barChart"):
			chart_data, chart_options = bar_chart(dataframe, chart_builder_input)
		else:
			context['error_message'] = "That analysis type hasn't been implemented yet"

		context['chart_type'] = chart_type
		context['chart_data'] = json.dumps(chart_data, cls=CustomJSONEncoder)
		context['chart_options'] = json.dumps(chart_options)

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

	### Need to make this build all chart options not just type

####################### Generate Query & Chart Options #######################

def pie_chart(dataframe, chart_builder_input):
	"Pie Chart"
	column_names = chart_builder_input["column_names"]
	row_names = chart_builder_input["row_names"]
	
	# Get either the column or row name (whichever was specified)
	column_name = (row_names[:1] or column_names[:1])[0]

	query_results, tmp = dataframe.query_results(
		"SELECT %s `key`, count(*) y FROM %s GROUP BY 1" 
		% (column_name, dataframe.db_table_name)
	);
	
	chart_data = list(query_results)
	chart_options = {}
	return chart_data, chart_options


def line_chart(dataframe, chart_builder_input):
	
	column_names = chart_builder_input["column_names"]
	row_names = chart_builder_input["row_names"]
	group_names = chart_builder_input["group_names"]
	
	if(group_names == []):
		query = "SELECT %s x, avg(%s) y FROM %s GROUP BY 1 ORDER BY 1" % (column_names[0], row_names[0], dataframe.db_table_name)
	else:
		query = "SELECT %s x, avg(%s) y, %s g FROM %s GROUP BY 1, 3 ORDER BY 1" % (column_names[0], row_names[0], group_names[0], dataframe.db_table_name)

	query_results, query_headings = dataframe.query_results(query);


	if(group_names == []):
		query_results_as_list = list(query_results)
		chart_data = [{"key": row_names[0], "values":  query_results_as_list}]
	else:
		# Build a dictionary where each unique group value is a key for an array of x/y values
		query_results_group_dict = {}
		for dict in query_results:
			if(dict['g'] in query_results_group_dict.keys()):
				query_results_group_dict[dict['g']].append({'x': dict['x'], 'y': dict['y']})
			else:
				query_results_group_dict[dict['g']] = []

		# Instantiate a list then create an array where each element has all x/y data for a group value
		chart_data = []
		for key in query_results_group_dict.keys():
			one_group_data = {'key': key, 'values': query_results_group_dict[key]}
			chart_data.append(one_group_data)

	chart_options = {
		"xaxis_label": column_names[0],
		"xaxis_type": 'date' if hasattr(chart_data[0]["values"][0]["x"], "isoformat") else 'other',
		"yaxis_label": "avg(" + row_names[0] + ")"
	}

	print("\n\nLine Chart Query: ")
	print(query)
	print("\n\nLine Chart Options: ")
	print(chart_options)
	print("\n\nLine Chart Data: ")
	print(chart_data)

	return chart_data, chart_options


def scatter_chart(dataframe, chart_builder_input):
	
	column_names = chart_builder_input["column_names"]
	row_names = chart_builder_input["row_names"]
	group_names = chart_builder_input["group_names"]
	size_names = chart_builder_input["size_names"][0] if chart_builder_input["size_names"] else 1

	if(group_names == []):
		query = "SELECT %s x, %s y, %s size FROM %s" % (column_names[0], row_names[0], size_names, dataframe.db_table_name)
	else:
		# Also include group as a column (note: converts to string to handle datetime serialization issues, remove this later)		
		query = "SELECT %s x, %s y, %s size, %s g FROM %s ORDER BY 4" % (column_names[0], row_names[0], size_names, group_names[0], dataframe.db_table_name)

	query_results, query_headings = dataframe.query_results(query)

	if(group_names == []):
		query_results_as_list = list(query_results)
		chart_data = [{"key": row_names[0], "values":  query_results_as_list}]	
	else:
		# Build a dictionary where each group value is a key for an array of x/y values		
		query_results_group_dict = {}
		for dict in query_results:
			if(dict['g'] in query_results_group_dict.keys()):
				query_results_group_dict[dict['g']].append({'x': dict['x'], 'y': dict['y'], 'size': dict['size']})
			else:
				query_results_group_dict[dict['g']] = []

		# Instantiate a list then create an array where each element has all x/y data for a group value
		chart_data = []
		for key in query_results_group_dict.keys():
			one_group_data = {'key': key, 'values': query_results_group_dict[key]}
			chart_data.append(one_group_data)
		
	chart_options = {
		"xaxis_label": column_names[0],
		"xaxis_type": row_names[0],
		"yaxis_label": row_names[0]
	}

	print("Scatter Chart Query: ")
	print(query)
	print("\n\nScatter Chart Options: ")
	print(chart_options)
	print("\n\nScatter Chart Data: ")
	print(chart_data)
	
	return chart_data, chart_options


def bar_chart(dataframe, chart_builder_input):
	
	column_names = chart_builder_input["column_names"]
	row_names = chart_builder_input["row_names"]
	group_names = chart_builder_input["group_names"]
	
	if(group_names):
		query = "SELECT %s x, sum(%s) y, %s g FROM %s GROUP BY 1, 3 ORDER BY 2 DESC LIMIT 20" % (column_names[0], row_names[0], group_names[0], dataframe.db_table_name )
	else:
		query = "SELECT %s label, sum(%s) value FROM %s GROUP BY 1 ORDER BY 2 DESC LIMIT 20" % (column_names[0], row_names[0], dataframe.db_table_name )

	query_results, query_headings = dataframe.query_results(query);

	if(group_names == []):
		query_results_as_list = list(query_results)
		chart_data = [{"key": row_names[0], "values":  query_results_as_list}]
	else:
		# Build a dictionary where each group value is a key for an array of x/y values		
		query_results_group_dict = {}
		for dict in query_results:
			print "\n\n" + json.dumps(query_results_group_dict) + "\n\n"
			if(dict['g'] in query_results_group_dict.keys()):
				query_results_group_dict[dict['g']].append({'x': dict['x'], 'y': dict['y']})
			else:
				query_results_group_dict[dict['g']] = []

		# Instantiate a list then create an array where each element has all x/y data for a group value
		chart_data = []
		for key in query_results_group_dict.keys():
			one_group_data = {'key': key, 'values': query_results_group_dict[key]}
			chart_data.append(one_group_data)


	chart_options = {
		"xaxis_label": column_names[0],
		"xaxis_type": row_names[0],
		"yaxis_label": "sum(" + row_names[0] + ")",
		"group_label": group_names[0] if group_names else ""
	}

	print("Bar Chart Query: ")
	print(query)
	print("\n\nBar Chart Options: ")
	print(chart_options)
	print("\n\nBar Chart Data: ")
	print(chart_data)
	
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
