from django.views.generic import TemplateView
from data.models import DataFrame
from django.http import HttpResponse
import json
from decimal import Decimal
import datetime

import sys
from pprint import pprint
from django.utils import timezone


# Move this later 		
class CustomJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if hasattr(obj, 'isoformat'): #handles both date and datetime objects
			print("\n\n\nGOT A DATE:")
			return obj.isoformat()
 		elif hasattr(obj, 'total_seconds'):
 			return str(obj)
		if isinstance(obj, Decimal):
			return float(obj)
		else:
			return json.JSONEncoder.default(self, obj)

####################### Chart Builder #######################

class ChartBuilderView(TemplateView):
	template_name = "chart_builder.html"

	def get(self, request, *args, **kwargs):
		context = super(ChartBuilderView, self).get_context_data(**kwargs)

		try:
			dataframe = DataFrame.objects.get(pk = request.GET.get('dataframe_id'))
		except Exception,e:
			context['debug'] = str(e)
			return self.render_to_response(context)
			
		context['dataframe'] = dataframe

		return self.render_to_response(context)

####################### Choose the right chart type #######################

def chart_selector(dataframe, chart_builder_input):
	ncols = len(chart_builder_input["column_names"])
	nrows = len(chart_builder_input["row_names"])
	
	datacols = dataframe.columns;

	if(ncols == 1):
		x_role = datacols[chart_builder_input["column_names"][0]]["Type"];
	
	if (ncols + nrows) == 1:
		return "pieChart"  
	elif (ncols == 1) and (nrows == 1):
		return "lineChart"  
	else:
		return "none"

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
	
	query = "SELECT %s x, avg(%s) y FROM %s GROUP BY 1 ORDER BY %s" % (column_names[0], row_names[0], dataframe.db_table_name, column_names[0] )
# 	query = "SELECT %s x, %s y FROM %s GROUP BY 1 ORDER BY %s" % (column_names[0], row_names[0], dataframe.db_table_name, column_names[0] )
	query_results, query_headings = dataframe.query_results(query);

	query_results_as_list = list(query_results)
	chart_data = [{"key": row_names[0], "values":  query_results_as_list}]

	print("\n\nLine Chart Query is: " + query)

	chart_options = {
		"xaxis_label": column_names[0],
		"xaxis_type": 'date' if hasattr(chart_data[0]["values"][0]["x"], "isoformat") else 'other',
		"yaxis_label": row_names[0]
	}

	return chart_data, chart_options

####################### Build Chart #######################

class AutoChartView(TemplateView):
	template_name = "autochart.html"

	def get(self, request, *args, **kwargs):
		context = super(AutoChartView, self).get_context_data(**kwargs)

		chart_builder_input = json.loads(request.GET.get("chart_builder_input"))
		dataframe_id = chart_builder_input["dataframe_id"]

		# Get the dataframe
		try:
			dataframe = DataFrame.objects.get(pk = dataframe_id)
		except Exception,e:
			context['debug'] = str(e)
			return self.render_to_response(context)

		chart_type = chart_selector(dataframe, chart_builder_input)
		# Create chart data & chart options function
		if(chart_type == "none"):
			chart_data = []
			chart_options = {}
		elif(chart_type == "pieChart"):
			chart_data, chart_options = pie_chart(dataframe, chart_builder_input)
		elif(chart_type == "lineChart"):
			chart_data, chart_options = line_chart(dataframe, chart_builder_input)
		else:
			context['error_message'] = "That analysis type hasn't been implemented yet"

		print("\n\nChart Data")
		print(chart_data)

		context['chart_type'] = chart_type
		context['chart_data'] = json.dumps(chart_data, cls=CustomJSONEncoder)
		context['chart_options'] = json.dumps(chart_options)

		print("\n\n chart_data_json: ")
		print(context['chart_data'])
		
		print("\n\n chart_type: ")
		print(context['chart_type'])
		
		print("\n\n chart_options: ")
		print(context['chart_options'])

		return self.render_to_response(context)

