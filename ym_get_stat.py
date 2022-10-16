# Получение статистики
def ym_get_stat(counter, limit, _date1, _date2, _metrics, _dimensions, _sort):
    params = dict(
        ids=counter,
        date1=_date1,
        date2=_date2,  # dt.date.today()
        metrics=_metrics,
        dimensions=_dimensions,
        sort=_sort,
        lang="ru",
        limit=limit,
        accuracy='full'
        # другие параметры -> https://yandex.ru/dev/metrika/doc/api2/api_v1/data.html
        )
    res_df = client.stats().get(params=params)

    count_iter = math.ceil(res_df['total_rows'] / limit)

    print('Необходимое кол-во итераций:', count_iter)
    if count_iter == 1:
        res_df = pd.DataFrame(res_df().to_dicts())
        print('Данные полностью скачены.')
    else:
        k = 0
        rep = res_df
        res_df = pd.DataFrame()
    
        for i in range(1, math.ceil(rep['total_rows'] / limit)+1):
            params = dict(
                ids=counter,
                date1=_date1,
                date2=_date2,  # dt.date.today()
                metrics=_metrics,
                dimensions=_dimensions,
                sort=_sort,
                lang="ru",
                limit=limit,
                accuracy='full',
                offset=1+k)
    
            print(f'....качаю с строки #{k}, итерация #{i}')
            k += limit
        
            report = client.stats().get(params=params)
    
            res_df = pd.concat([res_df, pd.DataFrame(report().to_dicts())])
    clear_output()
    print('Данные полностью скачены!')
    
    return res_df

# для форматирования времени
def to_time_str(df):
    time_int = round(df['Время на сайте'])
    return str(dt.timedelta(seconds=time_int))

# первая строка = заголовок
def row_to_header(df):
    df.columns = df.iloc[0]
    df = df[1:]
    return df
