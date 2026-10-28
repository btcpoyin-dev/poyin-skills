import json,urllib.request,time,datetime as dt
UA={'User-Agent':'Mozilla/5.0','Content-Type':'application/json'}
def get(u,d=None):
    r=urllib.request.Request(u,data=json.dumps(d).encode() if d else None,headers=UA)
    return json.load(urllib.request.urlopen(r,timeout=20))
T0=int(dt.datetime(2026,10,21).timestamp()); T1=int(dt.datetime(2026,10,29).timestamp())
DAYS=['10/%d'%d for d in range(21,29)];Q=555.8;V={}
def v(n): return V.setdefault(n,{'venue':n})
def hist(n,pairs):
    d={k:0.0 for k in DAYS}
    for ts,r in pairs:
        if T0<=ts<T1: d[dt.datetime.fromtimestamp(ts).strftime('%m/%d')]+=r*100
    x=v(n);x.update({k:round(d[k],4) for k in DAYS});x['sum8d%']=round(sum(d.values()),4)
def slip(lv,q):
    rem=q;c=0
    for px,sz in lv:
        t=min(rem,sz);c+=t*px;rem-=t
        if rem<=1e-9:return c/q,None
    return None,q-rem
def book(n,bids,asks):
    bids=sorted([(float(a),float(b)) for a,b in bids],reverse=True);asks=sorted([(float(a),float(b)) for a,b in asks])
    m=(bids[0][0]+asks[0][0])/2;x=v(n);x['spread%']=round((asks[0][0]-bids[0][0])/m*100,4)
    b,fb=slip(asks,Q);s,fs=slip(bids,Q)
    x['mkt_buy_slip%']=round((b-m)/m*100,4) if b else 'depth only %.1f'%(Q-fb)
    x['mkt_sell_slip%']=round((m-s)/m*100,4) if s else 'depth only %.1f'%(Q-fs)
    x['depth_bid_units']=round(sum(q for _,q in bids),1);x['depth_ask_units']=round(sum(q for _,q in asks),1)
def cur(n,iv,rp,mark,index):
    x=v(n);x.update({'interval_h':iv,'cur_rate%':round(rp,4),'per_h%':round(rp/iv,4),'mark':mark,'index':index})
    try:x['mark_vs_index%']=round((float(mark)/float(index)-1)*100,3)
    except Exception:pass
def safe(f,n):
    try:f()
    except Exception as e: v(n)['err']=v(n).get('err','')+repr(e)[:80]+';'
FEES={'Binance':(0.05,0.02),'OKX':(0.05,0.02),'Bybit':(0.055,0.02),'Gate':(0.05,0.02),'Bitget':(0.06,0.02),'MEXC':(0.02,0.0),'Bitunix':(0.06,0.02),'HTX':(0.05,0.02),'HL xyz':(0.0432,0.0144),'HL para':(0.0432,0.0144),'Aster':(0.035,0.01),'Lighter':(0.0,0.0)}
H='https://api.hyperliquid.xyz/info'
def hl(dex,n):
    hist(n,[(x['time']//1000,float(x['fundingRate'])) for x in get(H,{'type':'fundingHistory','coin':dex+':UNITREE','startTime':T0*1000})])
    m,c=get(H,{'type':'metaAndAssetCtxs','dex':dex});c=c[[a['name'] for a in m['universe']].index(dex+':UNITREE')]
    cur(n,1,float(c['funding'])*100,c['markPx'],c['oraclePx'])
    b=get(H,{'type':'l2Book','coin':dex+':UNITREE'})['levels'];book(n,[(x['px'],x['sz']) for x in b[0]],[(x['px'],x['sz']) for x in b[1]])
for dex,n in [('xyz','HL xyz'),('para','HL para')]: safe(lambda:hl(dex,n),n)
def bn(n,b):
    hist(n,[(x['fundingTime']//1000,float(x['fundingRate'])) for x in get(b+'/fapi/v1/fundingRate?symbol=UNITREEUSDT&limit=1000&startTime=%d'%(T0*1000))])
    p=get(b+'/fapi/v1/premiumIndex?symbol=UNITREEUSDT');iv=8
    try:iv=next(x['fundingIntervalHours'] for x in get(b+'/fapi/v1/fundingInfo') if x['symbol']=='UNITREEUSDT')
    except Exception:pass
    cur(n,iv,float(p['lastFundingRate'])*100,p['markPrice'],p['indexPrice'])
    d=get(b+'/fapi/v1/depth?symbol=UNITREEUSDT&limit=1000');book(n,d['bids'],d['asks'])
for n,b in [('Binance','https://www.binance.com'),('Aster','https://fapi.asterdex.com')]: safe(lambda:bn(n,b),n)
O='https://www.okx.com/api/v5'
def okx():
    p=[];a=''
    for _ in range(3):
        dd=get(O+'/public/funding-rate-history?instId=UNITREE-USDT-SWAP&limit=100'+a)['data']
        if not dd:break
        p+=[(int(x['fundingTime'])//1000,float(x['realizedRate'] or x['fundingRate'])) for x in dd];a='&after='+dd[-1]['fundingTime']
        if int(dd[-1]['fundingTime'])//1000<T0:break
    hist('OKX',p);f=get(O+'/public/funding-rate?instId=UNITREE-USDT-SWAP')['data'][0]
    iv=(int(f['nextFundingTime'])-int(f['fundingTime']))/3.6e6 if f.get('nextFundingTime') else 8
    cur('OKX',iv,float(f['fundingRate'])*100,get(O+'/public/mark-price?instType=SWAP&instId=UNITREE-USDT-SWAP')['data'][0]['markPx'],get(O+'/market/index-tickers?instId=UNITREE-USDT')['data'][0]['idxPx'])
    cv=float(get(O+'/public/instruments?instType=SWAP&instId=UNITREE-USDT-SWAP')['data'][0]['ctVal'])
    h=get(O+'/market/books?instId=UNITREE-USDT-SWAP&sz=400')['data'][0]
    book('OKX',[(x[0],float(x[1])*cv) for x in h['bids']],[(x[0],float(x[1])*cv) for x in h['asks']])
safe(okx,'OKX')
G='https://api.gateio.ws/api/v4/futures/usdt'
def gate():
    hist('Gate',[(x['t'],float(x['r'])) for x in get(G+'/funding_rate?contract=UNITREE_USDT&limit=200')])
    c=get(G+'/contracts/UNITREE_USDT');cur('Gate',c['funding_interval']/3600,float(c['funding_rate'])*100,c['mark_price'],c['index_price'])
    qm=float(c['quanto_multiplier']);d=get(G+'/order_book?contract=UNITREE_USDT&limit=200')
    book('Gate',[(x['p'],float(x['s'])*qm) for x in d['bids']],[(x['p'],float(x['s'])*qm) for x in d['asks']])
safe(gate,'Gate')
BG='https://api.bitget.com/api/v2/mix/market'
def bitget():
    hist('Bitget',[(int(x['fundingTime'])//1000,float(x['fundingRate'])) for x in get(BG+'/history-fund-rate?symbol=UNITREEUSDT&productType=usdt-futures&pageSize=100')['data']])
    f=get(BG+'/current-fund-rate?symbol=UNITREEUSDT&productType=usdt-futures')['data'][0]
    p=get(BG+'/symbol-price?symbol=UNITREEUSDT&productType=usdt-futures')['data'][0]
    cur('Bitget',float(f.get('fundingRateInterval') or 8),float(f['fundingRate'])*100,p['markPrice'],p['indexPrice'])
    d=get(BG+'/merge-depth?symbol=UNITREEUSDT&productType=usdt-futures&limit=max')['data'];book('Bitget',d['bids'],d['asks'])
safe(bitget,'Bitget')
M='https://contract.mexc.com/api/v1/contract'
def mexc():
    p=[]
    for pg in (1,2):p+=[(x['settleTime']//1000,float(x['fundingRate'])) for x in get(M+'/funding_rate/history?symbol=UNITREE_USDT&page_size=100&page_num=%d'%pg)['data']['resultList']]
    hist('MEXC',p);f=get(M+'/funding_rate/UNITREE_USDT')['data'];t=get(M+'/ticker?symbol=UNITREE_USDT')['data']
    cur('MEXC',f['collectCycle'],float(f['fundingRate'])*100,t['fairPrice'],t['indexPrice'])
    cv=float(get(M+'/detail?symbol=UNITREE_USDT')['data']['contractSize']);d=get(M+'/depth/UNITREE_USDT?limit=1000')['data']
    book('MEXC',[(x[0],x[1]*cv) for x in d['bids']],[(x[0],x[1]*cv) for x in d['asks']])
safe(mexc,'MEXC')
BU='https://fapi.bitunix.com/api/v1/futures/market'
def bitunix():
    hist('Bitunix',[(int(x['fundingTime'])//1000,float(x['fundingRate'])) for x in get(BU+'/get_funding_rate_history?symbol=UNITREEUSDT&limit=100')['data']])
    f=get(BU+'/funding_rate?symbol=UNITREEUSDT')['data'];cur('Bitunix',f['fundingInterval'],float(f['fundingRate']),f['markPrice'],f['indexPrice'])
    d=get(BU+'/depth?symbol=UNITREEUSDT&limit=max')['data'];book('Bitunix',d['bids'],d['asks'])
safe(bitunix,'Bitunix')
L='https://mainnet.zklighter.elliot.ai/api/v1'
def lighter():
    h=get(L+'/fundings?market_id=220&resolution=1h&start_timestamp=%d&end_timestamp=%d&count_back=300'%(T0,int(time.time())))
    v('Lighter')['lraw']=str(h)[:400];fs=h['fundings']
    hist('Lighter',[(int(x['timestamp']),(-1 if x.get('direction')=='short' else 1)*float(x['rate'])/100) for x in fs])
    r=[x for x in get(L+'/funding-rates')['funding_rates'] if x['exchange']=='lighter' and x['symbol']=='UNITREE']
    dd=(get(L+'/orderBookDetails?market_id=220').get('order_book_details') or [{}])[0]
    cur('Lighter',1,float(r[0]['rate'])*100/8 if r else float('nan'),dd.get('last_trade_price'),None)
    o=get(L+'/orderBookOrders?market_id=220&limit=250')
    book('Lighter',[(x['price'],x['remaining_base_amount']) for x in o['bids']],[(x['price'],x['remaining_base_amount']) for x in o['asks']])
safe(lighter,'Lighter')
v('Bybit')['note']='parent fills';v('HTX')['note']='parent fills'
for n,(t,m) in FEES.items():
    x=v(n);x['taker%']=t;x['maker%']=m
    try:x['roundtrip_taker%']=round(2*t+x['mkt_buy_slip%']+x['mkt_sell_slip%'],4)
    except Exception:pass
V['_ts']=time.strftime('%F %T');json.dump(V,open('unitree_all.json','w'),indent=1,ensure_ascii=False)
