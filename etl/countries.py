from urllib import urlopen 

from recon.interactive import interactive, SQLALoadMemory
from recon.local import CSVLocalEndpoint
import sqlaload as sl

COUNTRIES_URL = 'countrycodes.csv'

def integrate_countries(engine):
    fh = urlopen(COUNTRIES_URL)
    uri = lambda r: r['ISO-2']
    endpoint = CSVLocalEndpoint(fh, 'Country', uri_maker=uri)
    integrate_recon(engine, sl.get_table(engine, 'representative'), 
                    endpoint.reconcile,
                    'contactCountry',
                    'contactCountryName', 'contactCountryCode',
                    memory_name='recon_countryNames')
    integrate_recon(engine, sl.get_table(engine, 'countryOfMember'), 
                    endpoint.reconcile,
                    'countryOfMember',
                    'countryOfMemberName', 'countryOfMemberCode',
                    memory_name='recon_countryNames')

def integrate_recon(engine, table, qfunc, src_col, dst_name_col, dst_uri_col,
        min_score=None, limit=200, memory_name=None):
    if memory_name is None:
        memory_name = "recon_%s_%s" % (table.name, src_col)
    memory = SQLALoadMemory(engine, table=memory_name)
    for row in sl.distinct(engine, table, src_col):
        res = interactive(qfunc, row[src_col], min_score=min_score,
                memory=memory, limit=limit)
        if res is not None:
            #print row.get(src_col), " -> ", res.name.encode('utf-8'), res.score
            sl.upsert(engine, table, {src_col: row[src_col], dst_name_col: res.name, 
                      dst_uri_col: res.uri}, [src_col])

if __name__ == '__main__':
    import sys
    assert len(sys.argv)==2, "Usage: %s [engine-url]"
    engine = sl.connect(sys.argv[1])
    integrate_countries(engine)


