"""Reproducible synthetic demand scenario, not actual Amazon/Flipkart operations."""
from pathlib import Path
import sqlite3,json
import numpy as np,pandas as pd,plotly.express as px,plotly.graph_objects as go
ROOT=Path(__file__).resolve().parent
R=6371.0088

def distances(a,b):
    p1=np.radians(a[:,0])[:,None];l1=np.radians(a[:,1])[:,None]
    p2=np.radians(b[:,0])[None,:];l2=np.radians(b[:,1])[None,:]
    z=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin((l2-l1)/2)**2
    return 2*R*np.arcsin(np.sqrt(np.clip(z,0,1)))

def main():
    cities=pd.read_csv(ROOT/'data/cities.csv');wh=pd.read_csv(ROOT/'data/warehouses.csv')
    xy=cities[['latitude','longitude']].to_numpy();d=distances(xy,wh[['latitude','longitude']].to_numpy())
    weights=cities.daily_orders.to_numpy();baseline=d.min(axis=1)
    selected=[];best=baseline.copy()
    for _ in range(3):
        options=[]
        for j in range(len(cities)):
            if cities.iloc[j].city in set(wh.warehouse)|set(selected):continue
            new=np.minimum(best,distances(xy,xy[j:j+1]).ravel())
            options.append((np.dot(best-new,weights),j,new))
        gain,j,best=max(options,key=lambda x:x[0]);selected.append(cities.iloc[j].city)
    cities['baseline_km']=np.round(baseline,1);cities['optimized_km']=np.round(best,1)
    cities['distance_saved_km']=np.round(baseline-best,1)
    cities['nearest_baseline_warehouse']=[wh.iloc[i].warehouse for i in d.argmin(axis=1)]
    (ROOT/'outputs').mkdir(exist_ok=True)
    cities.to_csv(ROOT/'outputs/city_coverage.csv',index=False)
    old=float(np.average(baseline,weights=weights));new=float(np.average(best,weights=weights))
    metrics={'cities':len(cities),'existing_warehouses':len(wh),'recommended_warehouses':selected,'weighted_average_baseline_km':round(old,2),'weighted_average_optimized_km':round(new,2),'weighted_average_reduction_km':round(old-new,2),'weighted_reduction_percent':round(100*(old-new)/old,2),'cities_over_400km_before':int((baseline>400).sum()),'cities_over_400km_after':int((best>400).sum()),'demand_units':'illustrative daily orders','distance_type':'great-circle / Haversine, not driving'}
    (ROOT/'outputs/metrics.json').write_text(json.dumps(metrics,indent=2))
    with sqlite3.connect(ROOT/'outputs/warehouse_analysis.sqlite') as conn:
        cities.to_sql('city_coverage',conn,if_exists='replace',index=False);wh.to_sql('warehouses',conn,if_exists='replace',index=False)
    fig=go.Figure()
    fig.add_trace(go.Scattergeo(lat=cities.latitude,lon=cities.longitude,mode='markers+text',text=cities.city,textposition='top center',marker=dict(size=np.sqrt(cities.daily_orders)*.65,color=cities.distance_saved_km,colorscale='Viridis',showscale=True,colorbar=dict(title='Km saved')),name='Demand cities'))
    fig.add_trace(go.Scattergeo(lat=wh.latitude,lon=wh.longitude,mode='markers',marker=dict(symbol='square',size=13,color='royalblue'),name='Existing warehouses'))
    chosen=cities[cities.city.isin(selected)]
    fig.add_trace(go.Scattergeo(lat=chosen.latitude,lon=chosen.longitude,mode='markers',marker=dict(symbol='star',size=17,color='crimson'),name='Recommended warehouses'))
    fig.update_geos(fitbounds='locations',visible=False,showland=True,landcolor='#f1f5f9',showcountries=True)
    fig.update_layout(title='India warehouse coverage: synthetic demand scenario',height=750,margin=dict(l=20,r=20,t=80,b=20))
    fig.write_html(ROOT/'outputs/network_map.html',include_plotlyjs=True)
    bar=px.bar(cities.sort_values('distance_saved_km',ascending=False).head(15),x='city',y=['baseline_km','optimized_km'],barmode='group',title='Top 15 cities: nearest warehouse distance (km)')
    bar.write_html(ROOT/'outputs/coverage_comparison.html',include_plotlyjs=True)
    print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
