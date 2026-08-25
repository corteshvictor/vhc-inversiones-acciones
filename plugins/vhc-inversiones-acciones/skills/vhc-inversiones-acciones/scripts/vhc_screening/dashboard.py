"""Interactive HTML dashboard generation."""

import base64
import html
import json
from pathlib import Path

from . import i18n
from .constants import (
    ALERT_ALTMAN,
    ALERT_INSUFFICIENT,
    ALERT_M_SCORE,
    ALERT_ROIC,
    ALERT_TOO_CHEAP,
    ALERT_VALUE_TRAP,
    ALERT_WEAK_HEALTH,
    ALERT_WEAK_IMPROVEMENT,
    BUCKET_DEEP_DIVE,
    BUCKET_DISCARDED,
    BUCKET_NEUTRAL,
    BUCKET_WATCHLIST,
    CORE_COLUMNS,
    DEFAULT_ASSETS,
    NOT_AVAILABLE,
    PRICE_CHEAP,
    PRICE_EXPENSIVE,
    PRICE_MIXED,
    PRICE_VERY_CHEAP,
    QUALITY_EXCELLENT,
    QUALITY_GOOD,
    QUALITY_WEAK,
    SCREENING_VERSION,
    VERDICT_MEDIUM,
    VERDICT_NO,
    VERDICT_YES,
)
from .i18n import ENGLISH, SPANISH

DASH_CSS = """
:root{--paper:#FAF8F4;--card:#FFF;--rule:#E5DFD3;--rule2:#D3C9B7;--ink:#14243A;--body:#46566B;--muted:#5F6E80;
--quality:#3F7A4E;--quality-tint:#EAF1EA;--quality-border:#C6DCC9;--quality-dark:#2E6640;--health:#2B6CA3;--health-tint:#E6EEF7;--health-border:#C2D8EA;--health-dark:#205680;
--price:#A87516;--price-bright:#E0A32E;--price-tint:#F8F0DC;--price-border:#E4D2A8;--price-dark:#7E560F;
--risk:#B3453C;--risk-tint:#F8E9E6;--risk-border:#E8C8C4;--neutral:#6B7280;--neutral-border:#DAD4C7;--expensive:#3F4956;--expensive-tint:#E7E4DD;--expensive-border:#CFC8BA;
--track:#E4E8ED;--track-price:#E8E2D6;--serif:ui-serif,"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
--mono:ui-monospace,"SF Mono",Menlo,"Cascadia Mono",Consolas,monospace;--grid:26px minmax(0,1.5fr) 186px 104px 104px 116px 92px minmax(150px,1fr) 20px}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--paper);color:var(--body);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased;font-size:14px;padding:44px 42px 40px}
.wrap{max-width:1200px;margin:0 auto}
a{color:var(--price);text-decoration:none}a:hover{color:var(--price-dark);text-decoration:underline}
.eyebrow{font-size:10px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;color:var(--muted)}
.hr{height:1px;background:var(--rule2)}
header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px}
.lock{display:flex;align-items:center;gap:12px}
.lock img{width:38px;height:38px;border-radius:5px;flex:none;object-fit:cover}
.lock b{display:block;font-size:12.5px;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--ink)}
.lock span{display:block;font-size:11px;color:var(--muted);margin-top:2px}
.meta{font-family:var(--mono);font-size:10.5px;color:var(--muted);text-align:right;line-height:1.85}
.nav{display:flex;justify-content:space-between;align-items:center;gap:16px;margin:26px 0 0;flex-wrap:wrap}
.nav__tabs{display:flex;gap:6px}
.nav__lang{display:flex;border:1px solid var(--rule2);border-radius:4px;overflow:hidden;height:32px}
.nav__lang-btn{background:var(--card);border:0;border-left:1px solid var(--rule);color:var(--body);font-family:inherit;
font-weight:700;font-size:11px;letter-spacing:.08em;padding:0 12px;cursor:pointer}
.nav__lang-btn:first-child{border-left:0}
.nav__lang-btn[aria-selected=true]{background:var(--ink);color:#FFF}
.nav__lang-btn:focus-visible{outline:2px solid var(--price-bright);outline-offset:2px}
.nav__tab{background:transparent;border:1px solid var(--rule2);color:var(--body);border-radius:4px;padding:0 14px;height:32px;
font-family:inherit;font-weight:600;font-size:11.5px;cursor:pointer}
.nav__tab[aria-selected=true]{background:var(--ink);border-color:var(--ink);color:#FFF}
.nav__tab:focus-visible,.r__toggle:focus-visible,.tb__filter:focus-visible,.btn:focus-visible,.r__name a:focus-visible{outline:2px solid var(--price-bright);outline-offset:2px}
.hero{display:flex;justify-content:space-between;align-items:flex-end;gap:48px;margin-top:34px}
h1{font-family:var(--serif);font-size:54px;line-height:1.04;font-weight:400;letter-spacing:-.02em;color:var(--ink);
margin:12px 0 0;text-wrap:pretty}h1 span{color:var(--price)}
.hero__lede{font-size:14.5px;line-height:1.65;margin:14px 0 0;max-width:60ch;text-wrap:pretty}
.hero__lede b{color:var(--ink);font-weight:650}
.fnl{flex:none;width:360px}
.fnl__step{display:flex;align-items:center;gap:14px;margin-bottom:12px}
.fnl__num{font-family:var(--serif);font-size:26px;color:var(--ink);min-width:54px;flex:none;text-align:right;line-height:1}
.fnl__track{flex:1}.fnl__bar{height:10px;min-width:3px;border-radius:2px;background:#DDD7CA}
.fnl__label{font-size:10.5px;color:var(--muted);margin-top:5px}
.fnl__step--mid .fnl__bar{background:#A9B6A9}.fnl__step--end .fnl__num{color:var(--price)}.fnl__step--end .fnl__bar{background:var(--price-bright)}
.fnl__step--end .fnl__label{color:var(--ink);font-weight:600}
.dist{display:flex;height:8px;border-radius:2px;overflow:hidden;gap:2px;margin-top:40px}
.lg{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:16px;margin-top:14px}
.lg>div{border-top:1px solid var(--rule);padding-top:10px}
.lg__head{display:flex;align-items:baseline;gap:7px}
.lg i{width:7px;height:7px;border-radius:1px;flex:none;display:block}
.lg__value{font-size:20px;font-weight:650;color:var(--ink)}
.lg__pct{font-size:11px;color:var(--muted)}
.lg__title{font-size:11.5px;font-weight:650;color:var(--ink);margin-top:4px}
.lg__sub{font-size:11px;color:var(--muted);line-height:1.45;margin-top:2px}
.sect{display:flex;align-items:flex-end;justify-content:space-between;gap:24px 16px;margin:30px 0 4px;flex-wrap:wrap}
.sect>div:first-child{min-width:0;flex:1 1 320px}
.sect h2{font-family:var(--serif);font-size:27px;font-weight:400;color:var(--ink);letter-spacing:-.01em}
.sect__note{font-size:12.5px;color:var(--muted);margin-top:5px}
.sect__note b{font-weight:650}
.tb{display:flex;align-items:center;gap:8px;flex-wrap:wrap;min-width:0;max-width:100%}
.tb__search{display:flex;align-items:center;gap:7px;background:var(--card);border:1px solid var(--rule2);border-radius:4px;
padding:0 10px;height:32px;width:200px;min-width:0;max-width:100%}
.tb__search input{border:0;outline:0;background:transparent;font-family:inherit;font-size:12.5px;color:var(--ink);width:100%;min-width:0}
.tb__search input::placeholder{color:var(--muted)}
.tb__filters{display:flex;border:1px solid var(--rule2);border-radius:4px;overflow-x:auto;overflow-y:hidden;height:32px;min-width:0;max-width:100%;scrollbar-width:thin}
.tb__filter{background:var(--card);border:0;border-left:1px solid var(--rule);color:var(--body);font-family:inherit;flex:none;white-space:nowrap;
font-weight:600;font-size:11px;padding:0 12px;cursor:pointer;display:flex;align-items:center;gap:6px}
.tb__filter:first-child{border-left:0}
.tb__filter i{font-style:normal;color:var(--muted)}
.tb__filter[aria-selected=true]{background:var(--ink);color:#FFF;font-weight:650}
.tb__filter[aria-selected=true] i{color:rgba(255,255,255,.65)}
.card{background:var(--card);border:1px solid var(--rule);border-radius:5px;margin-top:16px}
.r__row{display:grid;grid-template-columns:var(--grid);gap:14px;align-items:center;width:100%;padding:13px 18px;
background:transparent;border:0;border-bottom:1px solid var(--rule);font-family:inherit;font-size:14px;text-align:left;color:inherit}
.r--exp .r__row{cursor:pointer}
.r__toggle{background:none;border:0;padding:0;cursor:pointer;color:#8A96A4;justify-self:end;
display:flex;align-items:center;justify-content:center;width:20px;height:20px}
.r__span{grid-column:3/9}
.r__head{border-bottom:1px solid var(--rule2);padding:11px 18px}
.r__head div{font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:var(--muted)}
.r:last-child .r__row{border-bottom:0}
.r--open .r__row{border-bottom-color:transparent;background:#FCFBF8}
.r__rank{font-family:var(--mono);font-size:11px;color:var(--muted)}
.r__name b{display:block;font-size:15px;font-weight:700;color:var(--ink);letter-spacing:.01em}
.r__name span{display:block;font-size:11.5px;color:var(--muted);margin-top:1px}
.r__score{display:flex;align-items:center;gap:12px}
.r__cells{display:flex;gap:11px}.r__cells div{display:flex;gap:3px}
.r__c{width:8px;height:12px;border-radius:1px;flex:none;display:block}
.r__c--q{background:var(--track)}.r__c--q.r__c--on{background:var(--quality)}
.r__c--h{background:var(--track)}.r__c--h.r__c--on{background:var(--health)}
.r__c--v{background:var(--track-price)}.r__c--v.r__c--on{background:var(--price-bright)}
.r__score em{font-style:normal;font-size:15px;font-weight:700;color:var(--ink)}
.r__score em small{font-size:11px;color:var(--muted);font-weight:500}
.chip{display:inline-block;padding:3px 8px;border-radius:3px;font-size:10px;font-weight:700;letter-spacing:.07em;
text-transform:uppercase;border:1px solid transparent;white-space:nowrap}
.chip--quality{color:var(--quality-dark);background:var(--quality-tint);border-color:var(--quality-border)}
.chip--quality-soft{color:var(--quality);border-color:var(--quality-border)}
.chip--health{color:var(--health-dark);background:var(--health-tint);border-color:var(--health-border)}
.chip--health-soft{color:var(--health);border-color:var(--health-border)}
.chip--price{color:var(--price-dark);background:var(--price-tint);border-color:var(--price-border)}
.chip--price-soft{color:var(--price);border-color:var(--price-border)}
.chip--neutral{color:var(--neutral);border-color:var(--neutral-border)}
.chip--risk{color:var(--risk);background:var(--risk-tint);border-color:var(--risk-border)}
.chip--calm{color:var(--expensive);background:var(--expensive-tint);border-color:var(--expensive-border)}
.r__up{font-size:12px;font-weight:600;text-align:right}
.nx{font-weight:inherit}
.r__up--pos{color:var(--quality)}.r__up--neg{color:var(--risk)}.r__up--flat{color:var(--muted)}
.r__none{color:var(--muted);font-size:12px}
.r__chev{width:14px;height:14px;transition:transform .18s}
.r--open .r__chev{transform:rotate(180deg);color:var(--price)}
.r__det{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;padding:4px 18px 20px 58px;
border-bottom:1px solid var(--rule);background:#FCFBF8}
.r__det[hidden]{display:none}
.gc{border-top:2px solid var(--rule2);padding-top:12px}
.gc--quality{border-top-color:var(--quality)}.gc--health{border-top-color:var(--health)}.gc--price{border-top-color:var(--price-bright)}
.gc h4{display:flex;align-items:baseline;justify-content:space-between;gap:10px;font-size:11px;font-weight:700;
letter-spacing:.1em;text-transform:uppercase}
.gc--quality h4{color:var(--quality)}.gc--health h4{color:var(--health)}.gc--price h4{color:var(--price)}
.gc h4 span{font-size:11px;font-weight:500;letter-spacing:0;text-transform:none;color:var(--muted)}
.gc__verdicts{display:flex;flex-wrap:wrap;gap:5px;margin:10px 0 12px}
.gc__metric{font-size:11px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:4px 12px;
padding:4px 0;border-bottom:1px solid #F0EBE1}
.gc__term{background:none;border:0;padding:0;font:inherit;color:inherit;cursor:help;text-align:left;
border-bottom:1px dotted var(--rule2)}
.gc__term:hover{color:var(--ink);border-bottom-color:var(--muted)}
.gc__term:focus-visible{outline:2px solid var(--price-bright);outline-offset:2px}
.chip .gc__term{border-bottom-color:currentColor;opacity:.85}
.gc__def{flex-basis:100%;font-size:11px;line-height:1.55;color:var(--muted);background:#FBF9F5;
border-left:2px solid var(--rule2);padding:7px 10px;margin:4px 0 2px;text-wrap:pretty}
.gc__def[hidden]{display:none}
.gs__head{font-size:11px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;
color:var(--muted);margin-top:22px}
.gs__list{margin-top:10px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px 28px}
.gs__item{border-top:1px solid var(--rule);padding-top:10px}
.gs__item dt{font-size:12.5px;font-weight:650;color:var(--ink)}
.gs__item dd{font-size:12.5px;line-height:1.6;color:var(--body);margin-top:4px;text-wrap:pretty}
.gc__metric:last-child{border-bottom:0}.gc__metric b{color:var(--ink);font-weight:650}
.gc__metric b.gc__val--pos{color:var(--quality)}.gc__metric b.gc__val--neg{color:var(--risk)}.gc__metric b.gc__val--flat{color:var(--ink)}
.hint{font-size:11.5px;color:var(--muted);padding:12px 18px;display:flex;justify-content:space-between;gap:16px}
.miss{padding:22px 18px;font-size:13px;color:var(--muted)}
.jump{background:none;border:0;padding:0;font:inherit;color:var(--price);font-weight:650;cursor:pointer;
border-bottom:1px solid var(--price-border)}
.jump:hover{color:var(--price-dark)}
.jump:focus-visible{outline:2px solid var(--price-bright);outline-offset:2px}
.empty{padding:26px 18px;font-size:13px;color:var(--muted)}
.warn{background:#F8E9E6;border:1px solid var(--risk-border);border-left:3px solid var(--risk);border-radius:4px;
padding:14px 18px;margin-top:26px;font-size:13px;line-height:1.55;color:var(--body)}
.warn b{color:var(--risk)}
.warn__cols{font-family:var(--mono);font-size:12px;color:var(--ink)}
.warn__sub{display:block;margin-top:4px;color:var(--muted);font-size:12.5px}
.gates{display:grid;grid-template-columns:186px repeat(3,minmax(0,1fr));margin-top:26px}
.gates__gate{padding:22px 24px;border-right:1px solid var(--rule)}
.gates__gate:first-child{padding-left:0}.gates__gate:last-child{border-right:0;padding-right:0}
.gates__head{display:flex;align-items:center;gap:8px;font-size:10px;letter-spacing:.14em;text-transform:uppercase;font-weight:700}
.gates__head i{width:8px;height:8px;border-radius:1px;flex:none;display:block}
.gates__gate p{font-size:13px;color:var(--muted);margin-top:8px;line-height:1.5}
.gates__num{font-family:var(--serif);font-size:34px;line-height:1;margin-top:16px}
.gates__num small{font-family:system-ui,sans-serif;font-size:12px;color:var(--muted);margin-left:8px}
.gates__bar{display:flex;gap:2px;height:5px;border-radius:2px;overflow:hidden;margin-top:10px;background:#E7E2D8}
.gates__bar i{display:block}
.gates__note{font-size:11px;color:var(--muted);margin-top:7px}
.gates--quality{color:var(--quality)}.gates--quality i{background:var(--quality)}.gates--health{color:var(--health)}.gates--health i{background:var(--health)}
.gates--price{color:var(--price)}.gates--price i{background:var(--price-bright)}
.gs{margin-top:34px}
.gs h3{font-family:var(--serif);font-size:22px;font-weight:400;color:var(--ink);letter-spacing:-.01em}
.gs p{font-size:13.5px;line-height:1.7;margin-top:8px;max-width:78ch;text-wrap:pretty}
.gs p b{color:var(--ink);font-weight:650}
.cats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 28px;margin-top:16px}
.cats__item{display:flex;gap:12px;align-items:flex-start;border-top:1px solid var(--rule);padding-top:10px}
.cats__item .chip{flex:none;margin-top:1px}
.cats__item p{font-size:12.5px;line-height:1.55;margin:0}
.btnrow{display:flex;gap:10px;justify-content:flex-end;margin-top:26px}
.btn{background:var(--card);border:1px solid var(--rule2);color:var(--body);border-radius:4px;padding:0 14px;height:32px;
font-family:inherit;font-weight:600;font-size:11.5px;cursor:pointer}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--rule2);display:flex;justify-content:space-between;
gap:32px;align-items:flex-start}
footer .legal{max-width:62ch;font-size:12.5px;line-height:1.65}
footer .legal b{color:var(--ink);font-weight:650}
footer .src{font-size:11.5px;color:var(--muted);margin-top:8px}
footer .social{display:flex;gap:18px;flex:none}
footer .social a{font-size:12px;font-weight:600}
[hidden]{display:none!important}
@media(max-width:699px){
body{padding:26px 18px 32px}
h1{font-size:38px}.hero{flex-direction:column;align-items:stretch;gap:28px}.fnl{width:auto}
.lg{grid-template-columns:repeat(2,minmax(0,1fr))}
.r__head{display:none}
.r__row{grid-template-columns:minmax(0,1fr) auto;gap:8px 12px;padding:14px 16px;row-gap:10px}
.r__rank{display:none}
.r__score{grid-column:1/3}
.r__span{grid-column:1/3}
.r__toggle{grid-row:1;grid-column:2;width:44px;height:44px;margin:-12px -12px -12px 0}
.r__row>div:nth-child(4),.r__row>div:nth-child(5),.r__row>div:nth-child(6){grid-column:1/3}
.r__row>div:nth-child(4)::before{content:"Calidad · ";font-size:10px;letter-spacing:.1em;text-transform:uppercase;
font-weight:700;color:var(--muted);margin-right:6px}
.r__row>div:nth-child(5)::before{content:"Salud · ";font-size:10px;letter-spacing:.1em;text-transform:uppercase;
font-weight:700;color:var(--muted);margin-right:6px}
.r__row>div:nth-child(6)::before{content:"Precio · ";font-size:10px;letter-spacing:.1em;text-transform:uppercase;
font-weight:700;color:var(--muted);margin-right:6px}
html[lang=en] .r__row>div:nth-child(4)::before{content:"Quality · "}
html[lang=en] .r__row>div:nth-child(5)::before{content:"Health · "}
html[lang=en] .r__row>div:nth-child(6)::before{content:"Price · "}
.r__up{grid-column:1/2;text-align:left}
.r__name{grid-row:1;grid-column:1}
.r__det{grid-template-columns:1fr;padding:4px 14px 18px}
.gates{grid-template-columns:1fr}.gates__gate{border-right:0;border-bottom:1px solid var(--rule);padding:18px 0}
.cats{grid-template-columns:1fr}
.nav__tab,.tb__filter,.btn,.nav__lang-btn{min-height:44px}
.tb__search{height:44px;width:100%;flex:1 1 100%}
.tb{width:100%;flex:1 1 100%}
.tb__filters{height:auto;-webkit-overflow-scrolling:touch}
.r__name a{display:inline-block;padding:4px 0}
}
@media(min-width:700px) and (max-width:1199px){
body{padding:30px 26px 34px}
h1{font-size:44px}
.hero{flex-direction:column;align-items:stretch;gap:28px}.fnl{width:auto}
.r__head{display:none}
.r__row{grid-template-columns:minmax(0,1fr) 104px 104px 116px 20px;gap:8px 12px;padding:13px 16px}
.r__rank{display:none}
.r__name{grid-row:1;grid-column:1}
.r__score{grid-row:2;grid-column:1}
.r__row>div:nth-child(4){grid-row:1;grid-column:2}
.r__row>div:nth-child(5){grid-row:1;grid-column:3}
.r__row>div:nth-child(6){grid-row:1;grid-column:4}
.r__row>div:nth-child(8){grid-row:2;grid-column:2/4;justify-self:start}
.r__up{grid-row:2;grid-column:4/5;text-align:right;align-self:center}
.r__toggle{grid-row:1;grid-column:5}
.r__span{grid-column:2/6}
.r__det{grid-template-columns:repeat(2,minmax(0,1fr));padding:4px 16px 18px 16px}
.gates{grid-template-columns:1fr 1fr}
.gates__gate:nth-child(2n){border-right:0}
.cats{grid-template-columns:1fr}
.gs__list{grid-template-columns:1fr}
}
@media print{
body{padding:0;background:#FFF}
.nav,.nav__tabs,.nav__lang,.tb,.btnrow,.r__chev,.hint,.tb__search,.tb__filters{display:none!important}
#guia,#resumen{display:block!important}
.pane[hidden]{display:none!important}
.r__det[hidden]{display:grid!important}
.gc__term{border-bottom:0}
.gc__def{display:none!important}
.card,.gates__gate,.gc{break-inside:avoid}
.r{break-inside:avoid}
a{color:var(--ink);text-decoration:none}
}
"""

_QUALITY_CHIP = {
    QUALITY_EXCELLENT: ("chip--quality", "Excelente", "Excellent"),
    QUALITY_GOOD: ("chip--quality-soft", "Buena", "Good"),
    QUALITY_WEAK: ("chip--neutral", "Débil", "Weak"),
}
_HEALTH_CHIP = {
    QUALITY_EXCELLENT: ("chip--health", "Excelente", "Excellent"),
    PRICE_MIXED: ("chip--health-soft", "Mixta", "Mixed"),
    QUALITY_WEAK: ("chip--neutral", "Débil", "Weak"),
}
_PRICE_CHIP = {
    PRICE_VERY_CHEAP: ("chip--price", "Muy barata", "Very cheap"),
    PRICE_CHEAP: ("chip--price-soft", "Barata", "Cheap"),
    PRICE_MIXED: ("chip--neutral", "Mixta", "Mixed"),
    PRICE_EXPENSIVE: ("chip--calm", "Cara", "Expensive"),
}
# The engine keeps emitting Spanish; the dashboard only renders a translation.
_ALERT_EN = {
    ALERT_VALUE_TRAP: "Possible value trap",
    ALERT_TOO_CHEAP: "Too cheap?",
    ALERT_M_SCORE: "M-Score",
    ALERT_ALTMAN: "Altman risk zone",
    ALERT_WEAK_HEALTH: "Excellent but weak health",
    ALERT_INSUFFICIENT: "Insufficient data",
    ALERT_ROIC: "Review ROIC/moat",
    ALERT_WEAK_IMPROVEMENT: "Weak improvement",
}
_SECTOR_EN = {"Financiero": "Financials", "Utilities": "Utilities"}
_BUCKET_EN = {
    BUCKET_DEEP_DIVE: "Deep Dive",
    BUCKET_WATCHLIST: "Watchlist",
    BUCKET_NEUTRAL: "Neutral",
    BUCKET_DISCARDED: "Discarded",
}
_LENS_CHIP = {
    VERDICT_YES: "chip--quality",
    VERDICT_MEDIUM: "chip--quality-soft",
    VERDICT_NO: "chip--neutral",
    NOT_AVAILABLE: "chip--neutral",
}
_RISK_ALERTS = (ALERT_VALUE_TRAP, ALERT_M_SCORE, ALERT_ALTMAN)

_BUCKET_TABS = (
    (BUCKET_DEEP_DIVE, "dd", BUCKET_DEEP_DIVE),
    (BUCKET_WATCHLIST, "wl", BUCKET_WATCHLIST),
    (BUCKET_NEUTRAL, "ne", BUCKET_NEUTRAL),
    (BUCKET_DISCARDED, "de", "Descartadas"),
)
_BUCKET_BLURB = {
    BUCKET_DEEP_DIVE: (
        "Cruzaron las tres puertas. Investigar a fondo no es comprar.",
        "They cleared the three gates. Researching deeply is not buying.",
    ),
    BUCKET_WATCHLIST: (
        "Grandes negocios sanos que hoy no pasan la puerta del precio.",
        "Great, healthy businesses that do not clear the price gate today.",
    ),
    BUCKET_NEUTRAL: (
        "No superan todas las puertas del método hoy.",
        "They do not clear every gate of the method today.",
    ),
    BUCKET_DISCARDED: (
        "No cumplen el método hoy. No es un pronóstico de precio.",
        "They do not meet the method today. This is not a price forecast.",
    ),
}


def escape_html(value) -> str:
    """Escapes any value coming from the export."""
    return html.escape(str(value), quote=True)


def format_metric(value, kind: str = "num") -> str:
    if value is None:
        return NOT_AVAILABLE
    formatters = {
        "pct": lambda item: f"{item:.1f} %",
        "up": lambda item: f"{item * 100:+.1f} %",
        "int": lambda item: f"{int(item)}",
        "num": lambda item: f"{item:.2f}",
    }
    return formatters.get(kind, formatters["num"])(value).replace(".", ",")


def chip_class(value: str) -> str:
    """Chip class for a method verdict or signal."""
    for table in (_QUALITY_CHIP, _HEALTH_CHIP, _PRICE_CHIP):
        if value in table:
            return table[value][0]
    return _LENS_CHIP.get(value, "chip--neutral")


# Glossary. Each definition describes the indicator and the threshold the
# method applies; it never suggests a buy or sell action.
_GLOSSARY = (
    (
        "q",
        "roic",
        "ROIC",
        "ROIC",
        (
            "Rentabilidad sobre el capital invertido: cuánto gana la empresa por cada "
            "unidad de capital que emplea en el negocio. La lente de Greenblatt pide "
            "≥ 20 % —actual y media de 5 años— para considerarlo un gran negocio, y "
            "lo marca como débil por debajo del 10 %."
        ),
        (
            "Return on invested capital: how much the company earns for each unit of "
            "capital it puts to work. The Greenblatt lens asks for ≥ 20 % —current "
            "and 5-year average— to call it a great business, and marks it weak below "
            "10 %."
        ),
    ),
    (
        "q",
        "roic5",
        "ROIC medio 5a",
        "5y average ROIC",
        (
            "El mismo ROIC promediado en cinco años. Distingue una rentabilidad "
            "sostenida de un año excepcional; si el actual cae por debajo del "
            "promedio, el informe avisa de que conviene revisar el foso competitivo."
        ),
        (
            "The same ROIC averaged over five years. It separates sustained returns "
            "from one exceptional year; if the current figure falls below the "
            "average, the report flags that the moat is worth reviewing."
        ),
    ),
    (
        "q",
        "roe",
        "ROE",
        "ROE",
        (
            "Rentabilidad sobre el patrimonio: lo que gana la empresa sobre el dinero "
            "de sus accionistas. La lente MSCI pide ≥ 15 % sin apalancamiento "
            "excesivo, y la marca como débil por debajo del 10 %."
        ),
        (
            "Return on equity: what the company earns on its shareholders' money. The "
            "MSCI lens asks for ≥ 15 % without excessive leverage, and marks it weak "
            "below 10 %."
        ),
    ),
    (
        "q",
        "gm",
        "Margen bruto",
        "Gross margin",
        (
            "Porcentaje que queda de cada venta tras el coste directo de producirla. "
            "La lente AQR lo cuenta como señal de rentabilidad a partir del 40 %."
        ),
        (
            "The share of each sale left after the direct cost of producing it. The "
            "AQR lens counts it as a profitability signal at or above 40 %."
        ),
    ),
    (
        "q",
        "eps",
        "BPA 5a",
        "5y EPS growth",
        (
            "Crecimiento medio del beneficio por acción en cinco años. AQR lo mira "
            "junto a las ventas: ambos positivos suman, uno negativo resta."
        ),
        (
            "Average earnings-per-share growth over five years. AQR reads it together "
            "with revenue: both positive adds, either one negative subtracts."
        ),
    ),
    (
        "q",
        "rev",
        "Ventas 5a",
        "5y revenue growth",
        (
            "Crecimiento anual compuesto de los ingresos en cinco años. Acompaña al "
            "BPA: crecer en beneficio sin crecer en ventas es una señal distinta."
        ),
        (
            "Compound annual revenue growth over five years. It travels with EPS: "
            "growing profit without growing sales is a different signal."
        ),
    ),
    (
        "h",
        "pio",
        "Piotroski",
        "Piotroski",
        (
            "Puntuación de 0 a 9 que resume nueve pruebas contables de rentabilidad, "
            "deuda y eficiencia. El método la cuenta como señal sana a partir de 7."
        ),
        (
            "A 0-to-9 score summarizing nine accounting tests of profitability, debt "
            "and efficiency. The method counts it as a healthy signal at or above 7."
        ),
    ),
    (
        "h",
        "altman",
        "Altman Z",
        "Altman Z",
        (
            "Modelo que estima la cercanía a una situación de insolvencia. Por encima "
            "de 3 es zona segura; por debajo de 1,81 el método clasifica la salud "
            "como débil directamente."
        ),
        (
            "A model estimating how close a company is to insolvency. Above 3 is the "
            "safe zone; below 1.81 the method classifies financial health as weak "
            "outright."
        ),
    ),
    (
        "h",
        "beneish",
        "Beneish M",
        "Beneish M",
        (
            "Modelo que estima la probabilidad de que las cuentas estén manipuladas. "
            "El método pide ≤ −1,78; por encima levanta la alerta M-Score. No prueba "
            "fraude: dice que los números merecen una segunda mirada."
        ),
        (
            "A model estimating the likelihood that the accounts have been "
            "manipulated. The method asks for ≤ −1.78; above that it raises the "
            "M-Score alert. It does not prove fraud: it says the numbers deserve a "
            "second look."
        ),
    ),
    (
        "h",
        "debt",
        "Deuda / Capital",
        "Debt / Capital",
        (
            "Qué parte de la financiación de la empresa es deuda. Por encima del 60 % "
            "la lente MSCI la considera apalancada."
        ),
        (
            "How much of the company's funding is debt. Above 60 % the MSCI lens treats "
            "it as leveraged."
        ),
    ),
    (
        "v",
        "evebit",
        "EV / EBIT",
        "EV / EBIT",
        (
            "Cuántas veces el beneficio operativo paga el valor total de la empresa, "
            "deuda incluida. Cuenta a favor entre 0 y 10, y en contra a partir de 20 "
            "o si es negativo."
        ),
        (
            "How many times operating profit covers the total value of the company, "
            "debt included. It counts in favor between 0 and 10, and against at or "
            "above 20 or if negative."
        ),
    ),
    (
        "v",
        "fcfy",
        "FCF Yield",
        "FCF Yield",
        (
            "Caja libre que genera la empresa por cada unidad de capitalización. "
            "Cuenta a favor desde el 4 % y en contra por debajo del 2 %."
        ),
        (
            "Free cash flow generated per unit of market capitalization. It counts in "
            "favor at or above 4 % and against below 2 %."
        ),
    ),
    (
        "v",
        "upside",
        "Precio vs fair value",
        "Price vs fair value",
        (
            "Distancia entre el precio actual y el valor razonable estimado por los "
            "modelos. Cuenta a favor a partir de +20 % y en contra por debajo de −10 "
            "%. Es una estimación, no un objetivo de precio."
        ),
        (
            "The gap between the current price and the fair value the models "
            "estimate. It counts in favor at or above +20 % and against below −10 %. "
            "It is an estimate, not a price target."
        ),
    ),
    (
        "v",
        "analysts",
        "Analistas",
        "Analysts",
        (
            "Etiqueta de consenso de analistas sobre el precio. Cuenta a favor si es "
            "infravalorada o de ganga, y en contra si es sobrevalorada."
        ),
        (
            "The analyst consensus label on price. It counts in favor when "
            "undervalued or a bargain, and against when overvalued."
        ),
    ),
    (
        "l",
        "greenblatt",
        "Greenblatt",
        "Greenblatt",
        (
            "Lente de calidad centrada en el ROIC actual y su media de cinco años: "
            "busca negocios que rentabilizan bien el capital de forma sostenida."
        ),
        (
            "A quality lens built on current ROIC and its five-year average: it looks "
            "for businesses that turn capital into returns consistently."
        ),
    ),
    (
        "l",
        "msci",
        "MSCI",
        "MSCI",
        (
            "Lente de calidad que combina rentabilidad sobre el patrimonio con "
            "apalancamiento: un ROE alto sostenido con deuda pesa distinto que sin "
            "ella."
        ),
        (
            "A quality lens combining return on equity with leverage: a high ROE held "
            "up by debt weighs differently from one that is not."
        ),
    ),
    (
        "l",
        "aqr",
        "AQR",
        "AQR",
        (
            "Lente de calidad con cuatro pilares —rentabilidad, crecimiento, "
            "seguridad y retribución al accionista—. Necesita al menos tres a favor y "
            "ninguno en contra."
        ),
        (
            "A quality lens with four pillars: profitability, growth, safety and "
            "shareholder payout. It needs at least three in favor and none against."
        ),
    ),
)
_GLOSSARY_BY_KEY = {entry[1]: entry for entry in _GLOSSARY}
_GLOSSARY_GROUPS = (
    ("l", "Las tres lentes de calidad", "The three quality lenses"),
    ("q", "Indicadores de calidad", "Quality indicators"),
    ("h", "Indicadores de salud financiera", "Financial health indicators"),
    ("v", "Indicadores de precio", "Price indicators"),
)


def _term(key: str) -> str:
    """Indicator label that reveals its definition inside the card."""
    _, _, spanish, english, _, _ = _GLOSSARY_BY_KEY[key]
    return (
        f'<button type="button" class="gc__term" data-g="{key}" '
        f'aria-expanded="false"{_en(english)}>{spanish}</button>'
    )


def _percent(part: int, total: int) -> float:
    return 100.0 * part / total if total else 0.0


def _thousands_es(value: int) -> str:
    """Formats an integer using a dot as the thousands separator."""
    return f"{value:,}".replace(",", ".")


def _thousands_en(value: int) -> str:
    """The same integer using the English convention, for translated text."""
    return f"{value:,}"


def _en_al(spanish: str, english: str) -> str:
    """Bilingual aria-label: Spanish in the DOM, English kept for the toggle."""
    return f' aria-label="{escape_html(spanish)}" data-en-al="{escape_html(english)}"'


def _en(text: str) -> str:
    """Attribute holding the English version; the DOM keeps the Spanish one."""
    return f' data-en="{escape_html(text)}"'


def _chip(table: dict, value: str) -> str:
    safe = escape_html(value)
    style, label, english = table.get(value, ("chip--neutral", safe, safe))
    return f'<span class="chip {style}"{_en(english)}>{label}</span>'


def _cells(filled: int, total: int, kind: str) -> str:
    marks = "".join(
        f'<span class="r__c r__c--{kind}{" r__c--on" if index < filled else ""}"></span>'
        for index in range(total)
    )
    return f"<div>{marks}</div>"


def _score(evaluation: dict) -> str:
    return (
        '<div class="r__score"><div class="r__cells">'
        f"{_cells(evaluation['quality_count'], 3, 'q')}"
        f"{_cells(evaluation['health_count'], 3, 'h')}"
        f"{_cells(evaluation['price_count'], 4, 'v')}"
        f"</div><em>{evaluation['score']}<small>/10</small></em></div>"
    )


def _tone(upside) -> str:
    """Green below fair value, coral above, neutral within one point."""
    if upside is None:
        return "flat"
    if upside >= 0.01:
        return "pos"
    if upside <= -0.01:
        return "neg"
    return "flat"


def _upside_cell(upside) -> str:
    if upside is None:
        return '<div class="r__up r__up--flat" data-en="N/A">N/D</div>'
    return f'<div class="r__up nx r__up--{_tone(upside)}">{format_metric(upside, "up")}</div>'


def _alert_en(note: str) -> str:
    """Alerts arrive joined by ' · '; each part is translated separately."""
    return " · ".join(_ALERT_EN.get(part, part) for part in note.split(" · "))


def _alert_cell(note: str) -> str:
    if note == "—":
        return '<div class="r__none">—</div>'
    style = (
        "chip--risk"
        if any(alert in note for alert in _RISK_ALERTS)
        else "chip--neutral"
    )
    return (
        f'<div><span class="chip {style}"{_en(_alert_en(note))}>'
        f"{escape_html(note)}</span></div>"
    )


def _missing_banner(missing: list[str]) -> str:
    if not missing:
        return ""
    columns = " · ".join(escape_html(column) for column in missing)
    english = (
        f"<b>{len(missing)} indicators are missing from your export</b> "
        "— add them in the InvestingPro screener and export again: "
        f'<span class="warn__cols">{columns}</span>'
        '<span class="warn__sub">They do not change the classification, but you lose '
        "context in the analysis.</span>"
    )
    return (
        f'<div class="warn"{_en(english)}>'
        f"<b>Faltan {len(missing)} indicadores en tu export</b> "
        "— agrégalos en el screener de InvestingPro y vuelve a exportar: "
        f'<span class="warn__cols">{columns}</span>'
        '<span class="warn__sub">No cambian la clasificación, pero pierdes contexto '
        "en el análisis.</span></div>"
    )


def _read_brand(assets_dir: Path) -> str:
    try:
        return base64.b64encode((assets_dir / "vhc-marca.webp").read_bytes()).decode()
    except OSError:
        return ""


def _ticker_link(evaluation: dict) -> str:
    ticker = escape_html(evaluation["ticker"])
    full_ticker = evaluation["metrics"].get("ft")
    if not full_ticker:
        return f"<b>{ticker}</b>"
    return (
        f'<b><a href="https://www.investing.com/pro/{escape_html(full_ticker)}" '
        f'target="_blank" rel="noopener">{ticker}</a></b>'
    )


def _moat_note(metrics: dict) -> str:
    declining = (
        metrics["roic"] is not None
        and metrics["roic5"] is not None
        and metrics["roic"] < metrics["roic5"]
    )
    return (
        '<div class="gc__verdicts"><span class="chip chip--neutral"'
        ' data-en="Current ROIC below its 5y average — review the moat">'
        "ROIC actual bajo su promedio 5a — revisar moat</span></div>"
        if declining
        else ""
    )


def _quality_card(evaluation: dict) -> str:
    metrics = evaluation["metrics"]
    lenses = " ".join(
        f'<span class="chip {_LENS_CHIP.get(value, "chip--neutral")}">{_term(key)}</span>'
        for key, value in zip(
            ("greenblatt", "msci", "aqr"), evaluation["lenses"], strict=True
        )
    )
    return f"""<div class="gc gc--quality"><h4><span{_en("Quality")}>Calidad</span><span{_en(str(evaluation["quality_count"]) + " of 3 lenses")}>{evaluation["quality_count"]} de 3 lentes</span></h4>
<div class="gc__verdicts">{lenses}</div>{_moat_note(metrics)}
<div class="gc__metric">{_term("roic")}<b>{format_metric(metrics["roic"], "pct")}</b></div>
<div class="gc__metric">{_term("roic5")}<b>{format_metric(metrics["roic5"], "pct")}</b></div>
<div class="gc__metric">{_term("roe")}<b>{format_metric(metrics["roe"], "pct")}</b></div>
<div class="gc__metric">{_term("gm")}<b>{format_metric(metrics["gm"], "pct")}</b></div>
<div class="gc__metric">{_term("eps")}<b>{format_metric(metrics["epsg"], "pct")}</b></div>
<div class="gc__metric">{_term("rev")}<b>{format_metric(metrics["revg"], "pct")}</b></div></div>"""


def _health_card(evaluation: dict) -> str:
    metrics = evaluation["metrics"]
    return f"""<div class="gc gc--health"><h4><span{_en("Financial health")}>Salud financiera</span><span{_en(str(evaluation["health_count"]) + " of 3 signals")}>{evaluation["health_count"]} de 3 señales</span></h4>
<div class="gc__verdicts">{_chip(_HEALTH_CHIP, evaluation["health"])}</div>
<div class="gc__metric">{_term("pio")}<b>{format_metric(metrics["pio"], "int")} / 9</b></div>
<div class="gc__metric">{_term("altman")}<b>{format_metric(metrics["alt"])}</b></div>
<div class="gc__metric">{_term("beneish")}<b>{format_metric(metrics["m"])}</b></div>
<div class="gc__metric">{_term("debt")}<b>{format_metric(metrics["dc"], "pct")}</b></div></div>"""


def _price_card(evaluation: dict) -> str:
    metrics = evaluation["metrics"]
    upside = evaluation["upside"]
    analyst_label = escape_html((metrics["lbl"] or NOT_AVAILABLE).title())
    return f"""<div class="gc gc--price"><h4><span{_en("Price")}>Precio</span><span{_en(str(evaluation["price_count"]) + " for · " + str(evaluation["contrary_count"]) + " against")}>{evaluation["price_count"]} a favor · {evaluation["contrary_count"]} en contra</span></h4>
<div class="gc__verdicts">{_chip(_PRICE_CHIP, evaluation["price"])}</div>
<div class="gc__metric">{_term("evebit")}<b>{format_metric(metrics["evebit"])}</b></div>
<div class="gc__metric">{_term("fcfy")}<b>{format_metric(metrics["fcfy"], "pct")}</b></div>
<div class="gc__metric">{_term("upside")}<b class="gc__val--{_tone(upside)}">{format_metric(upside, "up")}</b></div>
<div class="gc__metric">{_term("analysts")}<b>{analyst_label}</b></div></div>"""


def _row(position: int, evaluation: dict, prefix: str, detail: bool) -> str:
    search = escape_html(f"{evaluation['ticker']} {evaluation['name']}".lower())
    cells = (
        f'<span class="r__rank">{position:02d}</span>'
        f'<div class="r__name">{_ticker_link(evaluation)}'
        f"<span>{escape_html(evaluation['name'])}</span></div>"
        f"{_score(evaluation)}"
        f"<div>{_chip(_QUALITY_CHIP, evaluation['quality'])}</div>"
        f"<div>{_chip(_HEALTH_CHIP, evaluation['health'])}</div>"
        f"<div>{_chip(_PRICE_CHIP, evaluation['price'])}</div>"
        f"{_upside_cell(evaluation['upside'])}"
        f"{_alert_cell(evaluation['alerts'])}"
    )
    if not detail:
        return f'<div class="r" data-s="{search}"><div class="r__row">{cells}</div></div>\n'
    chevron = (
        '<svg class="r__chev" viewBox="0 0 20 20" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true"><path d="M6 8.5 10 12.5 14 8.5"/></svg>'
    )
    body = f"{_quality_card(evaluation)}{_health_card(evaluation)}{_price_card(evaluation)}"
    ticker = escape_html(evaluation["ticker"])
    return (
        f'<div class="r r--exp" data-s="{search}"><div class="r__row">{cells}'
        f'<button type="button" class="r__toggle" aria-expanded="false" '
        f'aria-controls="{prefix}{position}" '
        f"{_en_al(f'Ver los tres tribunales de {ticker}', f'View the three gates for {ticker}')}"
        f">{chevron}</button></div>"
        f'<div class="r__det" id="{prefix}{position}" hidden>{body}</div></div>\n'
    )


def _by_market_cap(evaluation: dict):
    """Sorts the Watchlist by descending market cap (dashboard only)."""
    market_cap = evaluation["metrics"].get("mcap")
    if market_cap is None:
        return 1, 0.0
    return 0, -market_cap


def _bucket_rows(
    evaluations: dict, order: list[int], bucket: str, prefix: str, detail: bool
) -> str:
    selected = [
        evaluations[key]
        for key in order
        if not evaluations[key]["fund"] and evaluations[key]["bucket"] == bucket
    ]
    if bucket == BUCKET_WATCHLIST:
        selected.sort(key=_by_market_cap)
    if not selected:
        return (
            f'<div class="empty"{_en("No company fell into this category.")}>'
            "Ninguna empresa quedó en esta categoría.</div>"
        )
    return "".join(
        _row(position, evaluation, prefix, detail)
        for position, evaluation in enumerate(selected, 1)
    )


def _omitted_rows(evaluations: dict, order: list[int]) -> str:
    selected = [
        evaluations[key] for key in order if evaluations[key].get("excluded_sector")
    ]
    if not selected:
        return (
            f'<div class="empty"{_en("No company fell into this category.")}>'
            "Ninguna empresa quedó en esta categoría.</div>"
        )
    rows = []
    for position, evaluation in enumerate(selected, 1):
        search = escape_html(f"{evaluation['ticker']} {evaluation['name']}".lower())
        sector = str(evaluation["excluded_sector"])
        rows.append(
            f'<div class="r" data-s="{search}"><div class="r__row">'
            f'<span class="r__rank">{position:02d}</span>'
            f'<div class="r__name"><b>{escape_html(evaluation["ticker"])}</b>'
            f"<span>{escape_html(evaluation['name'])}</span></div>"
            f'<div class="r__span"><span class="chip chip--neutral"'
            f"{_en(_SECTOR_EN.get(sector, sector))}>"
            f"{escape_html(sector)}</span></div></div></div>\n"
        )
    return "".join(rows)


def _panes(evaluations: dict, order: list[int], counts, omitted: int) -> str:
    head = (
        '<div class="r__row r__head"><div>#</div>'
        f"<div{_en('Company')}>Empresa</div><div{_en('Score')}>Puntaje</div>"
        f"<div{_en('Quality')}>Calidad</div><div{_en('Health')}>Salud</div>"
        f"<div{_en('Price')}>Precio</div>"
        f'<div style="text-align:right"{_en("vs Fair V.")}>vs Fair V.</div>'
        f"<div{_en('Note')}>Nota</div><div></div></div>"
    )
    panes = []
    for bucket, key, _label in _BUCKET_TABS:
        detail = bucket in (BUCKET_DEEP_DIVE, BUCKET_WATCHLIST)
        rows_hint = (
            f"<span{_en('click a row to see its three tribunals')}>"
            "clic en una fila para ver sus tres tribunales</span>"
            if detail
            else ""
        )
        hint = (
            f'<div class="hint">{rows_hint}'
            f"<span{_en('click a ticker to open its InvestingPro page')}>"
            "clic en el ticker para abrir su ficha en InvestingPro</span></div>"
        )
        rows = _bucket_rows(evaluations, order, bucket, f"d-{key}-", detail)
        hidden = "" if bucket == BUCKET_DEEP_DIVE else " hidden"
        panes.append(
            f'<div class="card pane" id="p-{key}" data-n="{counts[bucket]}"{hidden}>'
            f"{head}{rows}{hint}</div>"
        )
    om_hint = (
        f'<div class="hint"><span{
            _en(
                "Financials and utilities: the method sets them "
                "aside rather than applying thresholds that do not fit them"
            )
        }>'
        "Financieras y utilities: el método las aparta para no "
        "aplicarles umbrales que no les corresponden</span></div>"
    )
    panes.append(
        f'<div class="card pane" id="p-om" data-n="{omitted}" hidden>'
        f"{head}{_omitted_rows(evaluations, order)}{om_hint}</div>"
    )
    return "".join(panes)


def _toolbar(counts, omitted: int) -> str:
    buttons = []
    for bucket, key, label in _BUCKET_TABS:
        selected = "true" if bucket == BUCKET_DEEP_DIVE else "false"
        english = _BUCKET_EN[bucket]
        blurb_es, blurb_en = _BUCKET_BLURB[bucket]
        buttons.append(
            f'<button type="button" class="tb__filter" role="tab" aria-selected="{selected}" '
            f'data-p="p-{key}" data-l="{escape_html(label)}" '
            f'data-le="{escape_html(english)}" data-b="{escape_html(blurb_es)}" '
            f'data-be="{escape_html(blurb_en)}" data-total="{counts[bucket]}">'
            f"<span{_en(english)}>{escape_html(label)}</span> "
            f"<i>{_thousands_es(counts[bucket])}</i></button>"
        )
    buttons.append(
        '<button type="button" class="tb__filter" role="tab" aria-selected="false" '
        'data-p="p-om" data-l="Omitidas por método" '
        'data-le="Excluded by method" '
        'data-b="Financieras y utilities: el método las aparta en vez de '
        'clasificarlas mal." '
        'data-be="Financials and utilities: the method sets them aside rather than '
        'misclassifying them."'
        f' data-total="{omitted}">'
        f"<span{_en('Excluded')}>Omitidas</span> <i>{_thousands_es(omitted)}</i></button>"
    )
    return (
        '<div class="tb"><div class="tb__search">'
        '<svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" aria-hidden="true" style="color:var(--muted);flex:none">'
        '<circle cx="8.5" cy="8.5" r="5.5"/><path d="M12.6 12.6 17 17"/></svg>'
        '<input type="search" id="q" placeholder="Buscar ticker o empresa" '
        'data-en-ph="Search ticker or company" '
        'aria-label="Buscar ticker o empresa" '
        'data-en-al="Search ticker or company"></div>'
        f'<div class="tb__filters" role="tablist"{_en_al("Categorías", "Categories")}>'
        f"{''.join(buttons)}</div></div>"
    )


def _funnel(analyzed: int, excellent: int, deep: int) -> str:
    return (
        f'<div class="fnl"><div class="eyebrow" style="margin-bottom:14px"'
        f"{_en('The filter, in proportion')}>El filtro, en proporción</div>"
        f'<div class="fnl__step"><div class="fnl__num nx">{_thousands_es(analyzed)}</div><div class="fnl__track">'
        '<div class="fnl__bar" style="width:100%"></div>'
        f'<div class="fnl__label"{_en("Companies analyzed")}>Empresas analizadas</div></div></div>'
        f'<div class="fnl__step fnl__step--mid"><div class="fnl__num nx">{_thousands_es(excellent)}</div><div class="fnl__track">'
        f'<div class="fnl__bar" style="width:{_percent(excellent, analyzed):.1f}%"></div>'
        f'<div class="fnl__label"{_en("Solid quality and health")}>Calidad y salud sólidas</div></div></div>'
        f'<div class="fnl__step fnl__step--end"><div class="fnl__num nx">{_thousands_es(deep)}</div><div class="fnl__track">'
        f'<div class="fnl__bar" style="width:{_percent(deep, analyzed):.1f}%"></div>'
        f'<div class="fnl__label"{_en("Deep Dive · and at a good price")}>Deep Dive · además, a buen precio</div></div></div></div>'
    )


def _distribution(counts, omitted: int, analyzed: int, traps: int) -> str:
    entries = (
        (
            counts[BUCKET_DEEP_DIVE],
            "var(--price-bright)",
            (BUCKET_DEEP_DIVE, _BUCKET_EN[BUCKET_DEEP_DIVE]),
            ("Excelentes y a buen precio", "Excellent and fairly priced"),
        ),
        (
            counts[BUCKET_WATCHLIST],
            "#7FA98D",
            (BUCKET_WATCHLIST, _BUCKET_EN[BUCKET_WATCHLIST]),
            ("Excelentes esperando precio", "Excellent, waiting on price"),
        ),
        (
            counts[BUCKET_NEUTRAL],
            "#C3BCAD",
            (BUCKET_NEUTRAL, _BUCKET_EN[BUCKET_NEUTRAL]),
            ("No superan todas las puertas hoy", "They miss a gate today"),
        ),
        (
            counts[BUCKET_DISCARDED],
            "#D8A9A3",
            ("Descartadas", "Discarded"),
            (
                f"{_thousands_es(traps)} con nota de posible trampa",
                f"{traps:,} flagged as a possible value trap",
            ),
        ),
        (
            omitted,
            "#E2DCD0",
            ("Omitidas por método", "Excluded by method"),
            ("Financieras y utilities", "Financials and utilities"),
        ),
    )
    bars = "".join(
        f'<div style="flex:{max(value, 0)};background:{color}"></div>'
        for value, color, _title, _sub in entries
        if value
    )
    legend = "".join(
        f'<div><div class="lg__head"><i style="background:{color}"></i>'
        f'<span class="lg__value nx">{_thousands_es(value)}</span>'
        f'<span class="lg__pct">{_percent(value, analyzed):.1f} %</span></div>'
        f'<div class="lg__title"{_en(title[1])}>{title[0]}</div>'
        f'<div class="lg__sub"{_en(sub[1])}>{sub[0]}</div></div>'
        for value, color, title, sub in entries
    )
    return f'<div class="dist">{bars}</div><div class="lg">{legend}</div>'


def _gates(evaluations: dict, counts, excellent: int, classified: int) -> str:
    quality = sum(
        1
        for value in evaluations.values()
        if not value["fund"] and value["quality"] == QUALITY_EXCELLENT
    )
    deep = counts[BUCKET_DEEP_DIVE]
    watch = counts[BUCKET_WATCHLIST]
    rest = max(classified - quality, 0)
    lost = max(quality - excellent, 0)
    return f"""<div class="gates">
<div class="gates__gate"><div class="gates__num" style="color:var(--ink)"><b class="nx">{_thousands_es(classified)}</b></div>
<p{_en("classified companies, once the ones excluded by method are set aside")}>empresas clasificadas<br>tras apartar las omitidas por método</p></div>
<div class="gates__gate"><div class="gates__head gates--quality"><i></i><span{_en("Gate 1 · Quality")}>Puerta 1 · Calidad</span></div>
<p{_en("Is it a great business? Greenblatt, MSCI and AQR look at ROIC, ROE, debt and growth.")}>¿Es un gran negocio? Greenblatt, MSCI y AQR miran ROIC, ROE, deuda y crecimiento.</p>
<div class="gates__num gates--quality"><b class="nx">{_thousands_es(quality)}</b><small{_en("of " + _thousands_en(classified))}>pasan de {_thousands_es(classified)}</small></div>
<div class="gates__bar"><i style="flex:{quality};background:var(--quality)"></i><i style="flex:{rest}"></i></div>
<div class="gates__note"{_en(_thousands_en(rest) + " stop here")}>{_thousands_es(rest)} se quedan aquí</div></div>
<div class="gates__gate"><div class="gates__head gates--health"><i></i><span{_en("Gate 2 · Health")}>Puerta 2 · Salud</span></div>
<p{_en("Is it healthy and clean? Piotroski, Altman Z and Beneish M as the seatbelt.")}>¿Está sana y limpia? Piotroski, Altman Z y Beneish M como cinturón de seguridad.</p>
<div class="gates__num gates--health"><b class="nx">{_thousands_es(excellent)}</b><small{_en("of " + _thousands_en(quality))}>pasan de {_thousands_es(quality)}</small></div>
<div class="gates__bar"><i style="flex:{excellent};background:var(--health)"></i><i style="flex:{lost}"></i></div>
<div class="gates__note"{_en(_thousands_en(lost) + " stop here")}>{_thousands_es(lost)} se quedan aquí</div></div>
<div class="gates__gate"><div class="gates__head gates--price"><i></i><span{_en("Gate 3 · Price")}>Puerta 3 · Precio</span></div>
<p{_en("Is it cheap today? EV/EBIT, FCF yield, fair value and analyst consensus.")}>¿Está barata hoy? EV/EBIT, FCF yield, fair value y consenso de analistas.</p>
<div class="gates__num gates--price"><b class="nx">{_thousands_es(deep)}</b><small{_en("of " + _thousands_en(excellent))}>pasan de {_thousands_es(excellent)}</small></div>
<div class="gates__bar"><i style="flex:{deep};background:var(--price-bright)"></i><i style="flex:{watch};background:#7FA98D"></i></div>
<div class="gates__note"{_en("the other " + _thousands_en(watch) + " move to Watchlist")}>las otras {_thousands_es(watch)} pasan a {BUCKET_WATCHLIST}</div></div>
</div>"""


_GUIDE_CATS = (
    (
        "chip--price",
        (BUCKET_DEEP_DIVE, "Deep Dive"),
        (
            "Investigar a fondo. No significa comprar.",
            "Research it deeply. It does not mean buy.",
        ),
    ),
    (
        "chip--quality-soft",
        (BUCKET_WATCHLIST, "Watchlist"),
        (
            "Empresa excelente esperando un mejor precio.",
            "An excellent company waiting for a better price.",
        ),
    ),
    (
        "chip--neutral",
        (BUCKET_NEUTRAL, "Neutral"),
        ("No supera todas las puertas hoy.", "It misses a gate today."),
    ),
    (
        "chip--calm",
        ("Descartada", "Discarded"),
        (
            "No cumple el método hoy; no es un pronóstico de precio.",
            "It does not meet the method today; this is not a price forecast.",
        ),
    ),
    (
        "chip--neutral",
        ("Omitida por método", "Excluded by method"),
        (
            "Financiera o utility: sus umbrales no aplican.",
            "A financial or utility: these thresholds do not apply to it.",
        ),
    ),
    (
        "chip--risk",
        ("Alertas", "Alerts"),
        (
            "M-Score, Altman o trampa de valor: mirar antes de seguir.",
            "M-Score, Altman or value trap: look before going on.",
        ),
    ),
)


_SCORE_NOTE_EN = (
    'Score = <b style="color:var(--quality)">quality</b> (0–3) '
    '+ <b style="color:var(--health)">health</b> (0–3) '
    '+ <b style="color:var(--price)">price</b> (0–4). Each cell is one signal earned.'
)


# Notes shown in the "Nota" column, ordered by the severity the engine applies.
_ALERT_GUIDE = (
    (
        ALERT_INSUFFICIENT,
        "Insufficient data",
        "Faltan cinco o más métricas núcleo, así que el puntaje no es comparable.",
        "Five or more core metrics are missing, so the score is not comparable.",
    ),
    (
        ALERT_ALTMAN,
        "Altman risk zone",
        "Altman Z por debajo de 1,81.",
        "Altman Z below 1.81.",
    ),
    (
        ALERT_M_SCORE,
        "M-Score",
        (
            "Beneish M por encima de −1,78. No prueba fraude: pide una segunda "
            "mirada a la contabilidad."
        ),
        (
            "Beneish M above −1.78. It does not prove fraud: it asks for a second "
            "look at the accounts."
        ),
    ),
    (
        ALERT_VALUE_TRAP,
        "Possible value trap",
        "Calidad débil con precio barato o muy barato: barata por una razón.",
        "Weak quality with a cheap or very cheap price: cheap for a reason.",
    ),
    (
        ALERT_WEAK_HEALTH,
        "Excellent but weak health",
        (
            "Calidad excelente con salud financiera débil. La salud bloquea las "
            "listas de acción."
        ),
        (
            "Excellent quality with weak financial health, which excludes it "
            "from Deep Dive and Watchlist."
        ),
    ),
    (
        ALERT_TOO_CHEAP,
        "Too cheap?",
        (
            "Calidad excelente con upside desde +40 % o tres o más señales de "
            "precio a favor: comprobar por qué el mercado la castiga."
        ),
        (
            "Excellent quality with upside at or above +40 % or three or more "
            "price signals in favor: check why the market marks it down."
        ),
    ),
    (
        ALERT_WEAK_IMPROVEMENT,
        "Weak improvement",
        "Calidad excelente con Piotroski en 3 o menos.",
        "Excellent quality with Piotroski at or below 3.",
    ),
)


def _alerts_section() -> str:
    """Every note the report can raise, with the condition that triggers it."""
    items = "".join(
        f'<div class="gs__item"><dt><span class="chip {chip_class(spanish)}"'
        f"{_en(english)}>{escape_html(spanish)}</span></dt>"
        f"<dd{_en(english_definition)}>{spanish_definition}</dd></div>"
        for spanish, english, spanish_definition, english_definition in _ALERT_GUIDE
    )
    intro = (
        "La columna <b>Nota</b> avisa de lo que conviene mirar antes de seguir. "
        "Ninguna es un veredicto: señalan dónde detenerse. Cada empresa muestra "
        "como máximo las tres más graves, en este orden."
    )
    intro_en = (
        "The <b>Note</b> column flags what is worth checking before going on. "
        "None of them is a verdict: they point at where to stop. Each company "
        "shows at most the three most severe, in this order."
    )
    moat = (
        "Aparte de esta columna, la ficha de calidad muestra <b>ROIC actual bajo su "
        "promedio 5a — revisar moat</b> cuando el retorno sobre el capital cae por "
        "debajo de su media de cinco años."
    )
    moat_en = (
        "Beyond this column, the quality card shows <b>Current ROIC below its 5y "
        "average — review the moat</b> when return on invested capital falls below "
        "its five-year average."
    )
    return (
        f'<div class="gs"><h3{_en("Notes and alerts")}>Notas y alertas</h3>'
        f"<p{_en(intro_en)}>{intro}</p>"
        f'<dl class="gs__list">{items}</dl>'
        f"<p{_en(moat_en)}>{moat}</p></div>"
    )


def _glossary_section() -> str:
    """Complete, printable glossary inside the guide tab."""
    blocks = []
    for group, spanish, english in _GLOSSARY_GROUPS:
        items = "".join(
            f'<div class="gs__item"><dt{_en(entry[3])}>{entry[2]}</dt>'
            f"<dd{_en(entry[5])}>{entry[4]}</dd></div>"
            for entry in _GLOSSARY
            if entry[0] == group
        )
        blocks.append(
            f'<h4 class="gs__head"{_en(english)}>{spanish}</h4><dl class="gs__list">{items}</dl>'
        )
    intro = (
        "Qué mide cada indicador y qué umbral le aplica el método. "
        "Describen la medida, no una recomendación."
    )
    intro_en = (
        "What each indicator measures and which threshold the method applies to it. "
        "They describe the measure, not a recommendation."
    )
    joined = "".join(blocks)
    return (
        f'<div class="gs"><h3{_en("Glossary of indicators")}>Glosario de '
        f"indicadores</h3><p{_en(intro_en)}>{intro}</p>{joined}</div>"
    )


def _guide(evaluations: dict, counts, excellent: int, classified: int) -> str:
    cats = "".join(
        f'<div class="cats__item"><span class="chip {style}"{_en(label[1])}>{label[0]}</span>'
        f"<p{_en(text[1])}>{text[0]}</p></div>"
        for style, label, text in _GUIDE_CATS
    )
    return f"""<section id="guia" class="pane" hidden>
<div class="btnrow"><button type="button" class="btn" id="print"{_en("Print / save as PDF")}>Imprimir / guardar PDF</button></div>
<div class="gs"><h3{_en("The method, gate by gate")}>El método, puerta por puerta</h3>
<p{_en("A great company is not automatically a good investment. That is why the order matters: first whether the business is good, then whether it is healthy, and only at the end whether it is cheap. <b>Each gate lets fewer through.</b>")}>Una gran empresa no es automáticamente una buena inversión. Por eso el orden importa: primero
se pregunta si el negocio es bueno, después si está sano, y solo al final si está barato.
<b>Cada puerta deja pasar menos.</b></p>
{_gates(evaluations, counts, excellent, classified)}</div>
<div class="gs"><h3{_en("How to read the categories")}>Cómo leer las categorías</h3><div class="cats">{cats}</div></div>
<div class="gs"><h3{_en("The score")}>El puntaje</h3>
<p{_en("The score out of 10 is the sum of the three gates: <b>quality</b> (0–3 lenses), <b>health</b> (0–3 signals) and <b>price</b> (0–4 signals in favor). The ten cells beside each company show where its points come from, so two companies with the same total can tell different stories.")}>El puntaje sobre 10 es la suma de las tres puertas: <b>calidad</b> (0–3 lentes),
<b>salud</b> (0–3 señales) y <b>precio</b> (0–4 señales a favor). Las diez celdas junto a cada
empresa muestran de dónde salen sus puntos, así que dos empresas con el mismo total pueden
contar historias distintas.</p></div>
{_glossary_section()}
{_alerts_section()}
<div class="gs"><h3{_en("Educational, not advice")}>Educativo, no asesoría</h3>
<p{_en("This tool is not financial advice nor an investment recommendation. Fair values and analyst targets are estimates, not facts. The final decision requires your own analysis.")}>Esta herramienta no constituye asesoría financiera ni recomendación de inversión.
Los fair values y objetivos de analistas son estimaciones, no hechos. La decisión final
requiere análisis propio.</p></div></section>"""


_SCRIPT = r"""
(function(){
var panes=document.querySelectorAll('.pane[id^=p-]');
var fbtns=document.querySelectorAll('.tb__filter');
var title=document.getElementById('bt');
var blurb=document.getElementById('bb');
var LANG='es';
var TITLE={es:'Screening Cuantitativo — VHC Inversiones',
           en:'Quantitative Screening — VHC Inversiones'};
function head(){
  var on=document.querySelector('.tb__filter[aria-selected=true]')||fbtns[0];
  title.textContent=LANG==='en'?on.dataset.le:on.dataset.l;
  blurb.textContent=LANG==='en'?on.dataset.be:on.dataset.b;
}
function show(id){
  panes.forEach(function(p){p.hidden=p.id!==id});
  fbtns.forEach(function(b){b.setAttribute('aria-selected',String(b.dataset.p===id))});
  head();filter();
}
fbtns.forEach(function(b){b.addEventListener('click',function(){show(b.dataset.p)})});
function swapSep(t){
  return t.replace(/[.,]/g,function(c){return c==='.'?',':'.'}).replace(/\s%/g,'%');
}
function setLang(l){
  LANG=l;
  document.documentElement.lang=l;
  document.title=TITLE[l];
  document.querySelectorAll('[data-en]').forEach(function(el){
    if(el.dataset.es===undefined)el.dataset.es=el.innerHTML;
    el.innerHTML=l==='en'?el.dataset.en:el.dataset.es;
  });
  document.querySelectorAll('[data-en-ph]').forEach(function(el){
    if(el.dataset.esPh===undefined)el.dataset.esPh=el.placeholder;
    el.placeholder=l==='en'?el.dataset.enPh:el.dataset.esPh;
  });
  document.querySelectorAll('[data-en-al]').forEach(function(el){
    if(el.dataset.esAl===undefined)el.dataset.esAl=el.getAttribute('aria-label');
    el.setAttribute('aria-label',l==='en'?el.dataset.enAl:el.dataset.esAl);
  });
  document.querySelectorAll('.nx:not([data-en]), .gc__metric b').forEach(function(el){
    if(el.dataset.esN===undefined)el.dataset.esN=el.textContent;
    el.textContent=l==='en'?swapSep(el.dataset.esN):el.dataset.esN;
  });
  document.querySelectorAll('.nav__lang-btn').forEach(function(b){
    b.setAttribute('aria-selected',String(b.dataset.lang===l));
  });
  document.querySelectorAll('.gc__term[aria-expanded=true]').forEach(fill);
  head();filter();
}
document.querySelectorAll('.nav__lang-btn').forEach(function(b){
  b.addEventListener('click',function(){setLang(b.dataset.lang)});
});
var G=__GLOSSARY__;
function fill(btn){
  var host=btn.closest('.gc__metric')||btn.closest('.gc__verdicts')||btn.parentNode;
  var key=btn.dataset.g;
  var box=host.querySelector('.gc__def[data-for="'+key+'"]');
  if(!box){
    box=document.createElement('div');box.className='gc__def';box.dataset.for=key;
    host.appendChild(box);
  }
  box.textContent=(G[key]||{})[LANG]||'';
  return box;
}
document.addEventListener('click',function(e){
  var btn=e.target.closest('.gc__term');
  if(!btn)return;
  e.stopPropagation();
  var open=btn.getAttribute('aria-expanded')==='true';
  var box=fill(btn);
  btn.setAttribute('aria-expanded',String(!open));
  box.hidden=open;
});
var q=document.getElementById('q');
function grp3(n){return String(n).replace(/\B(?=(\d{3})+(?!\d))/g,'.')}
function fmtCount(n){var t=grp3(n);return LANG==='en'?swapSep(t):t}
function filter(){
  var term=(q.value||'').trim().toLowerCase();
  var hits=[],active=null;
  fbtns.forEach(function(b){
    var pane=document.getElementById(b.dataset.p),n=0;
    pane.querySelectorAll('.r').forEach(function(g){
      var hit=term===''||g.dataset.s.indexOf(term)>=0;
      if(hit)n++;
      if(!pane.hidden)g.hidden=!hit;
    });
    b.querySelector('i').textContent=fmtCount(term===''?+b.dataset.total:n);
    if(b.getAttribute('aria-selected')==='true')active=n;
    else if(term!==''&&n>0)hits.push(b);
  });
  elsewhere(term,active,hits);
}
function elsewhere(term,active,hits){
  document.querySelectorAll('.miss').forEach(function(m){m.remove()});
  var pane=document.querySelector('.pane[id^=p-]:not([hidden])');
  if(!pane)return;
  var hint=pane.querySelector('.hint');
  if(hint)hint.hidden=active===0;
  if(term===''||active!==0)return;
  var box=document.createElement('div');
  box.className='miss';
  if(!hits.length){
    box.textContent=(LANG==='en'?'No company matches ':'Ninguna empresa coincide con ')
      +'\u201c'+term+'\u201d.';
  }else{
    box.appendChild(document.createTextNode(
      LANG==='en'?'No matches here. Results in: ':'Aquí no hay coincidencias. Hay resultados en: '));
    hits.forEach(function(b,i){
      if(i)box.appendChild(document.createTextNode(' · '));
      var a=document.createElement('button');
      a.type='button';a.className='jump';
      a.textContent=(LANG==='en'?b.dataset.le:b.dataset.l)+' ('+b.querySelector('i').textContent+')';
      a.addEventListener('click',function(){show(b.dataset.p)});
      box.appendChild(a);
    });
  }
  pane.insertBefore(box,hint);
}
q.addEventListener('input',filter);
document.querySelectorAll('.r--exp').forEach(function(g){
  var b=g.querySelector('.r__toggle');
  g.addEventListener('click',function(e){
    if(e.target.closest('a,.r__det'))return;
    var open=b.getAttribute('aria-expanded')==='true';
    b.setAttribute('aria-expanded',String(!open));
    g.classList.toggle('r--open',!open);
    document.getElementById(b.getAttribute('aria-controls')).hidden=open;
  });
});
document.querySelectorAll('.nav__tab').forEach(function(t){
  t.addEventListener('click',function(){
    document.querySelectorAll('.nav__tab').forEach(function(o){o.setAttribute('aria-selected','false')});
    t.setAttribute('aria-selected','true');
    document.getElementById('resumen').hidden=t.dataset.t!=='resumen';
    document.getElementById('guia').hidden=t.dataset.t!=='guia';
  });
});
document.getElementById('print').addEventListener('click',function(){window.print()});
__BOOT__
})();
"""


def generate_dashboard(
    evaluations: dict,
    order: list[int],
    output_path: str | Path,
    export_name: str,
    run_date: str,
    counts,
    funds: int,
    excellent: int,
    traps: int,
    analyzed: int,
    missing: list[str] | None = None,
    assets_dir: str | Path = DEFAULT_ASSETS,
    language: str = SPANISH,
) -> None:
    """Generates a self-contained dashboard with no passive web dependencies."""
    missing_columns = missing or []
    missing_core = [column for column in missing_columns if column in CORE_COLUMNS]
    if missing_core:
        joined = ", ".join(missing_core)
        raise ValueError(i18n.text("dash_core_error", language, columns=joined))
    banner = _missing_banner(missing_columns)
    brand = _read_brand(Path(assets_dir))
    omitted = sum(1 for value in evaluations.values() if value.get("excluded_sector"))
    classified = max(analyzed - omitted, 0)
    deep = counts[BUCKET_DEEP_DIVE]
    definitions = json.dumps(
        {entry[1]: {"es": entry[4], "en": entry[5]} for entry in _GLOSSARY},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    english = language == ENGLISH
    boot = "setLang('en');" if english else ""
    title = "Quantitative Screening" if english else "Screening Cuantitativo"
    picked = ("false", "true") if english else ("true", "false")
    script = _SCRIPT.replace("__GLOSSARY__", definitions).replace("__BOOT__", boot)
    safe_export = escape_html(export_name)
    document = f"""<!DOCTYPE html>
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — VHC Inversiones</title>
<style>{DASH_CSS}</style></head><body><div class="wrap">
<header><div class="lock"><img src="data:image/webp;base64,{brand}" alt="VHC Inversiones">
<div><b>VHC Inversiones</b><span{_en("Quantitative stock screening")}>Screening cuantitativo de acciones</span></div></div>
<div class="meta">{safe_export}<br><span{_en("run")}>corrida</span> {run_date} · {SCREENING_VERSION} · {funds} <span{_en("funds excluded")}>fondos excluidos</span></div></header>
{banner}
<div class="nav"><div class="nav__tabs" role="tablist"{_en_al("Vistas", "Views")}>
<button type="button" class="nav__tab" role="tab" aria-selected="true" data-t="resumen"{_en("Summary")}>Resumen</button>
<button type="button" class="nav__tab" role="tab" aria-selected="false" data-t="guia"{_en("How to read this report")}>Cómo leer este informe</button></div>
<div class="nav__lang" role="group" aria-label="Idioma / Language">
<button type="button" class="nav__lang-btn" data-lang="es" aria-selected="{picked[0]}" lang="es">ES</button>
<button type="button" class="nav__lang-btn" data-lang="en" aria-selected="{picked[1]}" lang="en">EN</button></div></div>
<section id="resumen" class="pane">
<div class="hero"><div style="max-width:640px"><div class="eyebrow"{_en("Run result")}>Resultado de la corrida</div>
<h1><span{_en("From")}>De</span> <b class="nx">{_thousands_es(analyzed)}</b> <span{_en("stocks to")}>acciones a</span> <span><b class="nx">{_thousands_es(deep)}</b> <span{_en("candidates")}>candidatas</span></span></h1>
<p class="hero__lede"{_en("A candidate means <b>research it deeply</b>, not buy. The method asks in this order: is it a great business?, is it healthy?, and only at the end, is it cheap?")}>Candidata significa <b>investigar a fondo</b>, no comprar. El método pregunta en este orden:
¿es un gran negocio?, ¿está sano?, y solo al final, ¿está barato?</p></div>
{_funnel(analyzed, excellent, deep)}</div>
{_distribution(counts, omitted, analyzed, traps)}
<div class="hr" style="margin-top:36px"></div>
<div class="sect"><div><h2 id="bt">Deep Dive</h2><div class="sect__note" id="bb">{_BUCKET_BLURB[BUCKET_DEEP_DIVE][0]}</div>
<div class="sect__note"{_en(_SCORE_NOTE_EN)}>Puntaje = <b style="color:var(--quality)">calidad</b> (0–3) + <b style="color:var(--health)">salud</b> (0–3)
+ <b style="color:var(--price)">precio</b> (0–4). Cada celda es una señal ganada.</div></div>
{_toolbar(counts, omitted)}</div>
{_panes(evaluations, order, counts, omitted)}
</section>
{_guide(evaluations, counts, excellent, classified)}
<footer><div><div class="legal"{_en("An educational filtering tool. No category is an order to buy or sell, and <b>Discarded is not a price forecast</b>. Fair values and analyst targets are estimates, not facts.")}>Herramienta educativa de filtrado. Ninguna categoría es una orden de comprar
o vender, y <b>Descartada no es un pronóstico de precio</b>. Los fair values y objetivos de analistas
son estimaciones, no hechos.</div>
<div class="src"><span{_en("Source")}>Fuente</span>: InvestingPro · Skill VHC Inversiones · {SCREENING_VERSION} · <span{_en("run")}>corrida</span> {run_date}</div></div>
<div class="social"><a href="https://www.youtube.com/@VHCInversiones" target="_blank" rel="noopener">YouTube</a>
<a href="https://x.com/VHCInversiones" target="_blank" rel="noopener">X</a>
<a href="https://www.instagram.com/vhcinversiones" target="_blank" rel="noopener">Instagram</a></div></footer>
</div><script>{script}</script></body></html>"""
    Path(output_path).write_text(document, encoding="utf-8")
