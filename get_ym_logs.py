def get_logs_ym(date_start,
                date_end,
                source,
                field_list,
                logs_clear=False):
    params = {
    "fields": field_list,
    "source": source,
    "date1": date_start,
    "date2": date_end
    }
    
    
    # счетчик-таймер
    start_time = time.perf_counter()

    # тут происходит запрос и паолучение "объекта" из API, с ожидаем готовности отчета
    request = client.create().post(params=params)
    request_id = request["log_request"]["request_id"]
    report = client.download(requestId=request_id).get()
    
    # report = client.download(requestId=client.create().post(params=params)["log_request"]["request_id"]).get()

    # ответ приходит, в объекте несколько частей с данными - достаём их из каждой части и отгружаем в res_df
    res_df = pd.DataFrame()

    for part in report().parts():
        res_df = pd.concat([res_df, pd.DataFrame(part().to_dicts())])

    # название каждого столбца делим по ':', берём третье значение (индекс 2) = это заголовок
    res_df.columns = [i.split(':')[2] for i in res_df.columns]
    
    # # # сколько ушло времени + сколько строк получилось
    print('time loading:', round((time.perf_counter() - start_time)/60, 2), 'мин.')
    print('total row:', res_df.shape[0])
    print('id request:', request_id)
    
    if logs_clear==True:

        # удаляем за собой отчет из logs API (чтобы освободить очередь)
        header = {'Authorization': f'OAuth {token}'}
        url = f'https://api-metrika.yandex.net/management/v1/counter/{counter}/logrequest/{request_id}/clean'
        requests.post(url, headers=header)


          
    return res_df

    
