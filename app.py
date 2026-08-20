from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="DriftShield Local", page_icon="🌿", layout="wide")
DATA=Path("data/synthetic_pesticide_drift_registry.csv")
REQ=['record_id', 'field_code', 'spray_date', 'spray_start_time', 'crop_type', 'spray_area_acres', 'spray_method', 'wind_speed_kmh', 'wind_direction', 'wind_alignment_score', 'temperature_c', 'relative_humidity_pct', 'spray_duration_min', 'buffer_distance_m', 'home_distance_m', 'school_distance_m', 'water_body_distance_m', 'farm_distance_m', 'sensitive_site_density_score', 'weather_stability_score', 'spray_schedule_notice_score', 'drift_control_practice_score', 'inversion_signal_score', 'review_status']

st.markdown("""<style>
.stApp{background:#f6f8f7;color:#172b22}.block-container{max-width:1500px;padding:1.2rem 2rem 3rem}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #dce6df}
[data-testid="stSidebar"] *{color:#24382e!important}
.hero{background:linear-gradient(135deg,#fff,#eef8f0,#edf5f5);border:1px solid #d8e6dc;border-radius:28px;padding:30px 34px;margin-bottom:18px;box-shadow:0 14px 40px rgba(30,65,45,.07)}
.hero h1{color:#173d2a;font-size:2.55rem;letter-spacing:-.045em;margin:12px 0 8px}.hero p{color:#586d62;line-height:1.65}
.pill{display:inline-block;padding:7px 12px;margin-right:6px;border-radius:999px;background:#e8f5e9;border:1px solid #cfe4d2;color:#27613c;font-size:.72rem;font-weight:800}
.card{background:#fff;border:1px solid #dce7df;border-radius:20px;padding:20px;margin:12px 0;box-shadow:0 7px 22px rgba(32,61,45,.045)}
.info{background:#eff7f1;border:1px solid #d5e6da;border-radius:16px;padding:15px;color:#405d4c}
div[data-testid="stMetric"]{background:#fff;border:1px solid #dce7df;border-radius:18px;padding:12px 16px}
h2,h3{color:#203b2c!important}
</style>""",unsafe_allow_html=True)

def score(r):
    prox=np.mean([np.clip(100-float(r[c])/500*100,0,100) for c in ["home_distance_m","school_distance_m","water_body_distance_m","farm_distance_m"]])
    s=np.clip(.24*prox+.18*float(r.wind_alignment_score)+.13*float(r.weather_stability_score)+.10*float(r.inversion_signal_score)+.13*float(r.sensitive_site_density_score)+.07*np.clip(float(r.spray_area_acres)/30*100,0,100)+.05*np.clip(float(r.spray_duration_min)/60*100,0,100)+.06*(100-float(r.drift_control_practice_score))+.04*(100-float(r.spray_schedule_notice_score)),0,100)
    if s>=75: band="Critical Review"
    elif s>=55: band="High Review"
    elif s>=35: band="Moderate Review"
    else: band="Monitor"
    reasons=[]
    if prox>=60: reasons.append("nearby sensitive-site proximity")
    if float(r.wind_alignment_score)>=70: reasons.append("wind alignment")
    if float(r.sensitive_site_density_score)>=70: reasons.append("high sensitive-site density")
    if float(r.inversion_signal_score)>=65: reasons.append("inversion signal")
    if float(r.weather_stability_score)>=70: reasons.append("weather stability")
    if float(r.drift_control_practice_score)<60: reasons.append("limited drift-control signal")
    if float(r.spray_schedule_notice_score)<60: reasons.append("limited schedule-notice signal")
    return round(float(s),1),band,"; ".join(reasons) or "No strong priority signal under the local heuristic."

df=pd.read_csv(DATA)
missing=[c for c in REQ if c not in df.columns]
if missing: st.error("Missing required columns: "+", ".join(missing)); st.stop()
x=df.apply(score,axis=1,result_type="expand"); x.columns=["drift_screening_score","review_band","factor_explanation"]
df=pd.concat([df.reset_index(drop=True),x],axis=1)

st.sidebar.markdown("## 🌿 DriftShield Local")
st.sidebar.caption("Pesticide drift exposure screening support")
page=st.sidebar.radio("Workspace",["Exposure Command Center","Spray Event Explorer","Review Queue","Sensitive-Site Analysis","Local Data Lab","Responsible Use"])
st.sidebar.markdown("---"); st.sidebar.caption("100% local processing"); st.sidebar.caption("No external APIs"); st.sidebar.caption("Synthetic or authorized records only")

st.markdown("""<div class="hero"><span class="pill">LOCAL-FIRST</span><span class="pill">EXPOSURE SCREENING</span><span class="pill">EXPLAINABLE</span><span class="pill">HUMAN REVIEW</span>
<h1>🌿 DriftShield Local</h1><p><b>Pesticide Drift Exposure Monitor</b> — screen authorized spray-event records for potential drift-concern signals using wind conditions, spray activity, sensitive-site proximity, weather context, and mitigation indicators.</p>
<p>Results are operational screening signals. They do not estimate toxicological dose, individual health risk, legal compliance, or confirmed pesticide exposure.</p></div>""",unsafe_allow_html=True)

if page=="Exposure Command Center":
    a,b,c,d,e=st.columns(5); a.metric("Spray records",len(df)); b.metric("Average score",f"{df.drift_screening_score.mean():.0f}/100"); c.metric("High/Critical",int((df.drift_screening_score>=55).sum())); d.metric("Nearby-site signal",int((df.sensitive_site_density_score>=70).sum())); e.metric("Limited controls",int((df.drift_control_practice_score<60).sum()))
    l,r=st.columns(2)
    with l:
        q=df.groupby("field_code",as_index=False).drift_screening_score.mean()
        fig=px.bar(q,x="field_code",y="drift_screening_score",title="Average screening score by field"); fig.update_layout(template="plotly_white",height=380); st.plotly_chart(fig,use_container_width=True)
    with r:
        fig=px.scatter(df,x="wind_speed_kmh",y="drift_screening_score",size="sensitive_site_density_score",color="review_band",hover_name="record_id",title="Wind speed vs screening signal"); fig.update_layout(template="plotly_white",height=380); st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="info"><b>Interpretation:</b> Higher scores indicate combined operational signals that may justify additional review. They are not measurements of pesticide exposure.</div>',unsafe_allow_html=True)
    st.dataframe(df[["record_id","field_code","crop_type","spray_date","wind_speed_kmh","wind_direction","home_distance_m","school_distance_m","water_body_distance_m","drift_screening_score","review_band"]].sort_values("drift_screening_score",ascending=False),use_container_width=True,hide_index=True)

elif page=="Spray Event Explorer":
    st.subheader("🧭 Spray event explorer")
    f=st.selectbox("Select field",["All fields"]+sorted(df.field_code.unique())); v=df if f=="All fields" else df[df.field_code==f]
    a,b,c=st.columns(3); a.metric("Events",len(v)); b.metric("Mean score",f"{v.drift_screening_score.mean():.0f}/100"); c.metric("Mean wind",f"{v.wind_speed_kmh.mean():.1f} km/h")
    fig=px.scatter(v,x="home_distance_m",y="school_distance_m",size="drift_screening_score",color="review_band",hover_name="record_id",title="Sensitive-site proximity context"); fig.update_layout(template="plotly_white",height=500); st.plotly_chart(fig,use_container_width=True)
    st.dataframe(v[["record_id","crop_type","spray_method","wind_speed_kmh","wind_direction","temperature_c","relative_humidity_pct","spray_duration_min","drift_control_practice_score","drift_screening_score","review_band"]],use_container_width=True,hide_index=True)

elif page=="Review Queue":
    st.subheader("🎯 Authorized review queue")
    n=st.slider("Records to display",1,len(df),min(6,len(df)))
    for _,r in df.sort_values("drift_screening_score",ascending=False).head(n).iterrows():
        st.markdown(f'<div class="card"><h3>{r.record_id} · {r.field_code} — {r.review_band}</h3><b>Screening score:</b> {r.drift_screening_score:.0f}/100 &nbsp; | &nbsp; <b>Crop:</b> {r.crop_type}<br><b>Potential review factors:</b> {r.factor_explanation}</div>',unsafe_allow_html=True)

elif page=="Sensitive-Site Analysis":
    st.subheader("🏠 Sensitive-site proximity analysis")
    sc=["home_distance_m","school_distance_m","water_body_distance_m","farm_distance_m"]
    long=df[["record_id"]+sc].melt(id_vars="record_id",var_name="site_type",value_name="distance_m")
    fig=px.box(long,x="site_type",y="distance_m",points="all",title="Recorded distance to sensitive-site categories"); fig.update_layout(template="plotly_white",height=450); st.plotly_chart(fig,use_container_width=True)
    st.dataframe(pd.DataFrame([[c.replace("_distance_m","").replace("_"," ").title(),round(df[c].mean(),1),int((df[c]<=150).sum())] for c in sc],columns=["Site category","Mean distance (m)","Events ≤150 m"]),use_container_width=True,hide_index=True)

elif page=="Local Data Lab":
    st.subheader("📂 CSV validation and local replacement"); st.write("CSV files are processed locally and validated before replacement."); st.code(", ".join(REQ),language="text")
    up=st.file_uploader("Replace local pesticide-drift registry",type=["csv"])
    if up:
        try:
            new=pd.read_csv(up); miss=[c for c in REQ if c not in new.columns]
            if miss: st.error("Missing required columns: "+", ".join(miss))
            elif new.empty: st.error("The uploaded CSV contains no records.")
            else: new.to_csv(DATA,index=False); st.success(f"Validated and loaded {len(new):,} records."); st.rerun()
        except Exception as ex: st.error(f"CSV validation failed: {ex}")
    st.markdown("### Current local registry"); st.dataframe(df[REQ],use_container_width=True,hide_index=True)
    st.download_button("Download scored drift registry",df.to_csv(index=False).encode(),"pesticide_drift_scored.csv","text/csv")

else:
    st.subheader("🛡️ Responsible use")
    st.markdown("""<div class="card"><h3>Operational screening, not exposure or health assessment</h3><ul>
<li>Use synthetic or authorized spray-event and environmental records only.</li>
<li>The score is a transparent local heuristic based on supplied operational signals.</li>
<li>It does not calculate pesticide dose, toxicological exposure, or individual health risk.</li>
<li>Do not use the dashboard to identify, accuse, penalize, or publicly expose farms, applicators, or individuals.</li>
<li>Qualified agricultural, environmental-health, pesticide-safety, or regulatory professionals should review consequential cases.</li>
</ul></div>""",unsafe_allow_html=True)

st.markdown("---"); st.caption("DriftShield Local • 100% local processing • No external APIs • Pesticide drift decision support")
