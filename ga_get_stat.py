def initialize_analyticsreporting():
    '''
    from oauth
    '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])
    flow = client.flow_from_clientsecrets(
        json_path, 
        scope=SCOPES,
        message=tools.message_if_missing(json_path))
    
    storage = file.Storage(account_ga + '__token.dat')
    credentials = storage.get()
    
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
        http = credentials.authorize(http=httplib2.Http())
        analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)
        
    return analytics

####

def print_response(response):
    '''
    from set data
    '''
    list = []
    # get report data
    
    for report in response.get('reports', []):
        # set column headers
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])
        for row in rows:
            # create dict for each row
            dict = {}
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])
            # fill dict with dimension header (key) and dimension value (value)
            for header, dimension in zip(dimensionHeaders, dimensions):
                dict[header] = dimension
            # fill dict with metric header (key) and metric value (value)
            for i, values in enumerate(dateRangeValues):
                for metric, value in zip(metricHeaders, values.get('values')):
                    if ',' in value or '.' in value:
                        dict[metric.get('name')] = float(value)
                    else:
                        dict[metric.get('name')] = int(value)
            list.append(dict)
    df1 = pd.DataFrame(list)
    return df1

def get_report3(analytics, start_date, end_date, view_id, metrics, dimensions, page_token):
    '''
    from get data
    '''
    return analytics.reports().batchGet(
      body={
        'reportRequests': [{
          'viewId': view_id,
          'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
          'dimensions': dimensions,
          'metrics': metrics,
          'pageSize': 100_000,
          'samplingLevel': 'LARGE',
          'pageToken': page_token
        }]
      }).execute()
