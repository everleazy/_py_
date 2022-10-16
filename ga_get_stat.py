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

def get_report3_(analytics, start_date, end_date, view_id,M,D,PP_T):
      return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': view_id,
          'dateRanges': [{'startDate':start_date, 'endDate': end_date}],
          'dimensions':D,
          'metrics': M,
          'pageSize' :100000,
          'samplingLevel' : 'LARGE',
          'pageToken':PP_T 
        }]
      }
  ).execute()
    
def initialize_analyticsreporting_():
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

def ga_auth():
    try:
        analytics = initialize_analyticsreporting_()
        print(account_ga, ' - auth!')
        return analytics
    except:
        credentials = file.Storage(account_ga + '__token.dat').get()
        http = credentials.authorize(http=httplib2.Http())
        analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)
        print(account_ga, ' - token load!')
        return analytics
        
def get_ga_stat():
    need_dates = pd.date_range(start=start_date, end=end_date).astype('str').to_list()
    print('period:', start_date, '-', end_date, '// count day:', len(need_dates))

    ga_stat = pd.DataFrame()
    for iter_day in need_dates:
        response = get_report3(analytics,
                               iter_day, iter_day,
                               id_ga,
                               metrics_list,
                               dimension_list, '0')

        total_row = int(response['reports'][0]['data']['rowCount'])

        if total_row > 100_000:
            print('count iteration:', total_row // 100_000 + 1)
            for i in range(0, total_row // 100_000 + 1):
                i = str(0)
                res_df = pd.DataFrame()

                response = get_report3(analytics,
                                       iter_day,
                                       iter_day,
                                       id_ga,
                                       metrics_list,
                                       dimension_list, str(i))
                res_df = pd.concat([res_df, print_response(response)])
                ga_stat = pd.concat([res_df, ga_stat])

                i += 100_000
                if i > total_row:
                    i = total_row
        else:
            ga_stat = pd.concat([print_response(response), ga_stat])

        print(iter_day, '- done..')
        clear_output()


    # # ренейм заголовков
    ga_stat.columns = [i.split(':')[1] for i in ga_stat.columns]

    # # date to datetime
    ga_stat['date'] = pd.to_datetime(ga_stat['date'], format='%Y%m%d')


    print('---------------------\n', 'done! count row:', len(ga_stat), '\n---------------------')

    return ga_stat
