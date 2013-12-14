from django.views.generic import TemplateView
from data.models import DataFrame
from django.http import HttpResponse
from django.shortcuts import render

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
		
		# Get the dataframe from the ID passed in the url
		try:
			dataframe = DataFrame.objects.get(pk = chart_builder_input["dataframe_id"])
		except Exception,e:
			context['debug'] = str(e)
			return self.render_to_response(context)

		# Choose a Chart Type
		chart_type = chart_selector(dataframe, chart_builder_input)
		
		if(chart_type is None):
			return self.render_to_response(context)
		
		# Generate a Query
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
			return self.render_to_response(context)

		context['chart_type'] = chart_type
		context['chart_data'] = json.dumps(chart_data, cls=CustomJSONEncoder)
		context['chart_options'] = json.dumps(chart_options) if chart_options else {}

		print("\n\nChart Data: ")
		pprint.pprint(chart_data)
		print("\n\nChart Query: ")
		pprint.pprint(query)
		print("\n\nChart Options: ")
		pprint.pprint(chart_options)
		
		return self.render_to_response(context)

####################### View - AutoFilter #######################

class AutoFilterView(TemplateView):
	# Placeholder template name, should be overwritten with appropriate name later
	template_name = 'autofilter-text.html'
	
	def get(self, request, *args, **kwargs):
		context = super(AutoFilterView, self).get_context_data(**kwargs)

		# Get input values from URL params
		dataframe_id = request.GET.get("dataframe_id")
		column_name = request.GET.get("column_name")
	
		# Get the dataframe from the ID passed in the url
		try:
			dataframe = DataFrame.objects.get(pk = dataframe_id)
		except Exception,e:
			context['debug'] = str(e)
			return self.render_to_response(context)

		column = dataframe.columns[column_name]
	
		if(column['type_category'] == 'character'):
			template_name = 'autofilter-text.html'
		if(column['type_category'] == 'numeric'):
			template_name = 'autofilter-numeric.html'
		if(column['type'] == 'date'):
			template_name = 'autofilter-date.html'

		return render(request, template_name, context)

####################### View - Prediction Popover #######################

class PredictionPopoverView(TemplateView):
	# Placeholder template name, should be overwritten with appropriate name later

	def get(self, request, *args, **kwargs):
		template_name = 'prediction_popover.html'
		context = super(PredictionPopoverView, self).get_context_data(**kwargs)
		
		# Get input values from URL params
		dataframe_id = request.GET.get("dataframe_id")
		column_name = request.GET.get("column_name")
	
		# Get the dataframe from the ID passed in the url
		try:
			dataframe = DataFrame.objects.get(pk = dataframe_id)
		except Exception,e:
			context['debug'] = str(e)
			return self.render_to_response(context)

		context['dataframe_nrow'] = dataframe.nrow

		return render(request, template_name, context)

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
	elif (ncols == 1) and (nrows >= 1) and (col_datatype == "time") and (row_datatype == "numeric"):
		return "lineChart"
	elif (ncols ==1) and (nrows == 1) and (col_datatype == "character") and (row_datatype == "numeric"):
		return "barChart"
	elif (ncols == 1) and (nrows == 1) and (col_datatype == "numeric") and (row_datatype == "numeric"):
		return "scatterChart"  
	else:
		return None

####################### Query Builder #######################

def query_builder(dataframe, chart_type, chart_builder_input):
	
	column_names = chart_builder_input["column_names"]
	row_names = chart_builder_input["row_names"]
	group_names = chart_builder_input["group_names"]
	size_names = chart_builder_input["size_names"][0] if chart_builder_input["size_names"] else None
	filter_clauses = chart_builder_input["filter_clauses"]

	# Query Where
	if(filter_clauses):
		query_where = "WHERE " + 'AND '.join(filter_clauses) + " "
	else:
		query_where = ""

	# Query Aggregate Functions & Groups
	query_group_by = ""

	if(chart_type in "pieChart"):
		column_names = column_names if column_names else row_names		
		return "SELECT %s `key`, count(*) y FROM %s %s GROUP BY 1 ORDER BY 2 LIMIT 20" % (column_names[0], dataframe.db_table_name, query_where)
	elif(chart_type in ("lineChart", "barChart")):
		row_aggregate_functions = ['avg'] * len(row_names)
		query_group_by = "GROUP BY %s " % column_names[0]
		query_group_by += ", %s " % group_names[0] if group_names else ""
	elif(chart_type == "scatterChart"):
		row_aggregate_functions = [''] * len(row_names)
	
	# Query Select
	query_select = "SELECT "
	query_select += "%s g, " % group_names[0] if group_names else ""
	query_select += "%s size, " % size_names if size_names else ""
	
	for row_name in row_names:
		query_select += "%s(%s) %s, " % (row_aggregate_functions.pop(), row_name, row_name)
	query_select += "%s x " % column_names[0] if column_names else ""

	# Query From
	query_from = "FROM %s " % dataframe.db_table_name

	# Query 
	query = query_select + query_from + query_where + query_group_by

	print query
	return query

####################### Generate Query & Chart Options #######################

def get_chart_data(dataframe, query_results, chart_builder_input):

	column_names = chart_builder_input["column_names"]
	row_names = chart_builder_input["row_names"]
	group_names = chart_builder_input["group_names"]
	size_names = chart_builder_input["size_names"][0] if chart_builder_input["size_names"] else None

	if(group_names):
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
			y_key = row_names[0]
			if(size_names):
				query_results_group_dict[dict['g']].append({'x': dict['x'], 'y': dict[y_key], 'size': dict['size']})
			else:
				query_results_group_dict[dict['g']].append({'x': dict['x'], 'y': dict[y_key]})

	else:
		query_results_group_dict = {}

		for row_name in row_names:			
			query_results_group_dict[row_name] = []

		for query_row in query_results:		
			query_row_x = query_row.pop('x')
			for row_element_key in query_row.keys():
				if 'size' in query_row.keys():	
					if(row_element_key != 'size'):
						query_results_group_dict[row_element_key].append({'x': query_row_x, 'y': query_row[row_element_key], 'size': query_row['size']})
				else:
					query_results_group_dict[row_element_key].append({'x': query_row_x, 'y': query_row[row_element_key]})

	chart_data = []
	for key in query_results_group_dict.keys():
		one_group_data = {'key': key, 'values': query_results_group_dict[key]}
		chart_data.append(one_group_data)

	# Should pass function rather than using avg later
	chart_options = {
		"xaxis_label": column_names[0],
		"xaxis_type": dataframe.columns[column_names[0]]["type"],
		"yaxis_label": "avg(" + row_names[0] + ")",
		"size_label": size_names if size_names else "",
		"group_label": group_names[0] if group_names else "",
		"show_legend": len(chart_data) < 15
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
