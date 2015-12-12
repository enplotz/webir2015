MOST_CITED_BY_FIELD = 'WITH a as (SELECT unnest(fields_of_study) as field, id, name, cited FROM authors) '+\
                      ' SELECT id, au.name, field, cited FROM ('+\
                      ' SELECT id, name, field, rank() OVER (PARTITION BY field ORDER BY cited DESC)'+\
                      ' FROM a WHERE cited IS NOT NULL) sub_query JOIN authors au USING (id)'+\
                      ' WHERE rank = 1;'

def top_authors_m(measure,limit):
    if measure >= 7:
        addendum = ''
        if measure == 8: # last 5 years
            addendum = 'AND d.year >= (EXTRACT(YEAR FROM NOW())-5)'
        return 'SELECT a.name, a.id, COUNT(*) AS measure FROM authors a, documents d WHERE d.author_id= a.id ' +  addendum +  ' GROUP BY a.id ORDER BY measure DESC LIMIT ' + str(limit)
    return 'SELECT name,id, measures['+str(measure)+'] AS measure FROM authors WHERE measures IS NOT NULL ORDER BY measures['+str(measure)+'] DESC LIMIT ' + str(limit)

def avg_cite_sql(fields):
    sql = 'WITH ' + \
          'sub_authors AS ( ' + \
          'SELECT * FROM authors WHERE fields_of_study @> ARRAY[' + \
          ', '.join(map(lambda f: '\'{}\''.format(f), fields)) + \
          ']::varchar[] AND cited IS NOT NULL AND measures IS NOT NULL' + \
          '  ),' + \
          '    unnested AS (' + \
          '      SELECT id, generate_series(1, 6), unnest(measures) FROM sub_authors),' + \
          '    t1 AS (' + \
          '      SELECT generate_series, avg(unnest) AS average, NULL as avg_cited FROM unnested GROUP BY generate_series ORDER BY generate_series),' + \
          '  t2 as (SELECT NULL::numeric[] as array_agg , avg(cited) as avg_cited FROM sub_authors GROUP BY sub_authors.fields_of_study)' + \
          'SELECT array_agg(average) as avg_measures, min(t2.avg_cited) as avg_cited FROM t1, t2;'
    return sql
