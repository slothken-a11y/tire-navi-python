import streamlit as st
import pandas as pd
import math
import re

# =========================================================================
# ⚙️ ページ設定
# =========================================================================
st.set_page_config(page_title="Tire-Navi 2026", page_icon="🚗", layout="wide")

# カスタムCSSを注入して全体のデザインを調整
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #1e293b; font-weight: 800; }
    .stSelectbox label, .stSlider label, .stCheckbox label, .stRadio label { font-weight: bold; color: #334155; }
    hr { margin-top: 1.5rem; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# 📊 マスターデータ定義 (内部の商品・性能マスタ)
# =========================================================================
BRAND_MASTER = {
    "軽自動車": [
        {"maker": "ブリヂストン", "name": "REGNO GR-Leggera", "rank": "松", "safety": 5, "comfort": 5, "wet": 4, "eco": 4, "life": 5000, "desc": "軽自動車に究極の静粛性と乗り心地を"},
        {"maker": "ミシュラン", "name": "ENERGY SAVER 4", "rank": "竹", "safety": 5, "comfort": 4, "wet": 5, "eco": 4, "life": 6000, "desc": "雨の日の安心感と圧倒的なロングライフ性能"},
        {"maker": "ブリヂストン", "name": "ECOPIA NH200C", "rank": "竹", "safety": 4, "comfort": 4, "wet": 4, "eco": 5, "life": 5500, "desc": "新車装着同等性能で燃費と寿命のバランスが良い"},
        {"maker": "グッドイヤー", "name": "RVF02", "rank": "竹", "safety": 4, "comfort": 4, "wet": 4, "eco": 4, "life": 5300, "desc": "背の高い軽自動車でもふらつきを抑える専用設計"},
        {"maker": "ブリヂストン", "name": "NEWNO", "rank": "梅", "safety": 4, "comfort": 4, "wet": 4, "eco": 4, "life": 5000, "desc": "基本性能をしっかり抑えたスタンダードタイヤ"},
        {"maker": "グッドイヤー", "name": "EG01", "searchNames": ["EG01", "EG02"], "rank": "梅", "safety": 3, "comfort": 3, "wet": 3, "eco": 4, "life": 5000, "desc": "コストを抑えつつ基本性能を備えたスタンダード"},
        {"maker": "クムホ", "name": "ｸﾑﾎ ES31", "rank": "梅", "safety": 3, "comfort": 3, "wet": 3, "eco": 3, "life": 4500, "desc": "圧倒的な低価格で経済性を最優先"}
    ],
    "コンパクト": [
        {"maker": "ブリヂストン", "name": "REGNO GR-X3", "searchNames": ["GR-X3", "GR-X III", "GR-X2"], "rank": "松", "safety": 5, "comfort": 5, "wet": 5, "eco": 4, "life": 5500, "desc": "乗用車用タイヤの最高峰。静粛性と走行性能の両立"},
        {"maker": "ミシュラン", "name": "PRIMACY 4+", "rank": "松", "safety": 5, "comfort": 5, "wet": 5, "eco": 4, "life": 6000, "desc": "履き始めから履き替え時まで続くウェット性能と長寿命"},
        {"maker": "ブリヂストン", "name": "ECOPIA NH200C", "rank": "竹", "safety": 4, "comfort": 4, "wet": 4, "eco": 5, "life": 5500, "desc": "燃費と寿命、雨天性能を高次元でバランス"},
        {"maker": "グッドイヤー", "name": "EG02", "searchNames": ["EG01", "EG02"], "rank": "竹", "safety": 4, "comfort": 4, "wet": 4, "eco": 4, "life": 5200, "desc": "高い経済性と環境性能を両立したエコタイヤ"},
        {"maker": "ピレリ", "name": "POWERGY", "rank": "梅", "safety": 4, "comfort": 3, "wet": 4, "eco": 3, "life": 4800, "desc": "ウェットグリップ性能に優れ、コスパ抜群"},
        {"maker": "クムホ", "name": "ｸﾑﾎ ES31", "rank": "梅", "safety": 3, "comfort": 3, "wet": 3, "eco": 3, "life": 4500, "desc": "お求めやすい価格ながら低燃費性能も確保"}
    ],
    "ミニバン": [
        {"maker": "ブリヂストン", "name": "REGNO GRV II", "searchNames": ["GRV2", "GRV II", "GR-X3 Type RV"], "rank": "松", "safety": 5, "comfort": 5, "wet": 5, "eco": 4, "life": 5200, "desc": "広い車内でも会話が弾む。ミニバン特有のふらつきも抑制"},
        {"maker": "グッドイヤー", "name": "RVF02", "rank": "竹", "safety": 5, "comfort": 4, "wet": 4, "eco": 4, "life": 5500, "desc": "偏摩耗を抑え、ミニバンに必要な剛性と静粛性を確保"},
        {"maker": "ブリヂストン", "name": "ECOPIA NH200", "rank": "竹", "safety": 4, "comfort": 4, "wet": 4, "eco": 5, "life": 5300, "desc": "ミニバン専用設計で、雨の日でも安心、さらに長持ち"},
        {"maker": "ミシュラン", "name": "PRIMACY 4+", "searchNames": ["PRIMACY SUV+", "PRIMACY 4+"], "rank": "竹", "safety": 5, "comfort": 4, "wet": 5, "eco": 4, "life": 6000, "desc": "重量級のミニバンでも安定した走りと長寿命を実現"},
        {"maker": "ピレリ", "name": "POWERGY", "rank": "梅", "safety": 4, "comfort": 3, "wet": 4, "eco": 3, "life": 4800, "desc": "高いウェット性能で重量のあるミニバンでも安心"},
        {"maker": "クムホ", "name": "SOLUS TA71", "searchNames": ["TA71", "TA51a"], "rank": "梅", "safety": 3, "comfort": 3, "wet": 4, "eco": 3, "life": 4500, "desc": "コストを抑えてミニバンに必要な基本性能をカバー"}
    ],
    "セダン・クーペ": [
        {"maker": "ブリヂストン", "name": "REGNO GR-X3", "searchNames": ["GR-X3", "GR-X III", "GR-X2"], "rank": "松", "safety": 5, "comfort": 5, "wet": 5, "eco": 4, "life": 5500, "desc": "最高級の静粛性と滑らかな乗り心地で、上質な移動空間を演出"},
        {"maker": "ミシュラン", "name": "PRIMACY 4+", "rank": "松", "safety": 5, "comfort": 5, "wet": 5, "eco": 5, "life": 6500, "desc": "濡れた路面でも安心感が続く、ウェットブレーキ性能と圧倒的な寿命"},
        {"maker": "グッドイヤー", "name": "EAGLE LS EXE", "searchNames": ["LS EXE", "EXE"], "rank": "竹", "safety": 4, "comfort": 4, "wet": 4, "eco": 4, "life": 5200, "desc": "特殊コンパウンド採用で低燃費性能と操縦安定性を両立"},
        {"maker": "ピレリ", "name": "POWERGY", "rank": "梅", "safety": 4, "comfort": 3, "wet": 4, "eco": 3, "life": 4800, "desc": "コストを抑えつつ欧州性能。ウェットグリップに優れる"},
        {"maker": "クムホ", "name": "ECSTA PS71", "searchNames": ["PS71", "ES31"], "rank": "梅", "safety": 4, "comfort": 3, "wet": 4, "eco": 3, "life": 4600, "desc": "高速安定性とウェット性能に優れたスポーツコンフォート"}
    ],
    "SUV": [
        {"maker": "ブリヂストン", "name": "ALENZA LX100", "searchNames": ["LX100"], "rank": "松", "safety": 5, "comfort": 5, "wet": 4, "eco": 4, "life": 5500, "desc": "SUV専用設計。驚くほどの静かさとふらつきにくさを実現"},
        {"maker": "ミシュラン", "name": "PRIMACY SUV+", "rank": "松", "safety": 5, "comfort": 5, "wet": 5, "eco": 4, "life": 6000, "desc": "SUV特有のふらつきを抑え、濡れた路面でも高い制動力を発揮"},
        {"maker": "グッドイヤー", "name": "EfficientGrip SUV HP01", "searchNames": ["HP01", "MAXGUARD"], "rank": "竹", "safety": 4, "comfort": 4, "wet": 4, "eco": 4, "life": 5200, "desc": "オンロードでの快適性と低燃費を両立したスタンダードSUV。"},
        {"maker": "ピレリ", "name": "SCORPION VERDE", "rank": "竹", "safety": 4, "comfort": 4, "wet": 4, "eco": 4, "life": 5000, "desc": "環境に配慮しつつ、SUVに必要な安定性と寿命を確保"},
        {"maker": "クムホ", "name": "CRUGEN HP71", "searchNames": ["HP71"], "rank": "梅", "safety": 4, "comfort": 4, "wet": 4, "eco": 3, "life": 4800, "desc": "SUVに求められる静粛性と高速走行性能を低価格で提供"}
    ],
    "バン・商用車": [
        {"maker": "ブリヂストン", "name": "ECOPIA R710", "searchNames": ["R710"], "rank": "松", "safety": 5, "comfort": 3, "wet": 4, "eco": 5, "life": 7000, "desc": "働く車に最適な低燃費性能と圧倒的な寿命を両立"},
        {"maker": "グッドイヤー", "name": "CARGO PRO", "searchNames": ["CARGO", "CARGOPRO"], "rank": "竹", "safety": 4, "comfort": 3, "wet": 3, "eco": 4, "life": 6500, "desc": "ビジネスを支える高い経済性と、摩耗しても維持する安全性能"},
        {"maker": "クムホ", "name": "Portran KC53", "searchNames": ["KC53"], "rank": "梅", "safety": 3, "comfort": 2, "wet": 3, "eco": 3, "life": 6000, "desc": "高耐荷重と長寿命性能を兼ね備えた高コスパ・ビジネスタイヤ"}
    ],
    "軽トラ・軽バン": [
        {"maker": "ブリヂストン", "name": "ECOPIA R710", "searchNames": ["R710"], "rank": "松", "safety": 5, "comfort": 3, "wet": 4, "eco": 5, "life": 7000, "desc": "軽バン・軽トラ専用。低燃費で非常に長持ち"},
        {"maker": "グッドイヤー", "name": "CARGO PRO", "searchNames": ["CARGO", "CARGOPRO"], "rank": "竹", "safety": 4, "comfort": 3, "wet": 3, "eco": 4, "life": 6500, "desc": "泥道や農道でも頼もしいトラクションと経済性"},
        {"maker": "ブリヂストン", "name": "K370", "rank": "梅", "safety": 3, "comfort": 2, "wet": 3, "eco": 3, "life": 5000, "desc": "基本性能をしっかり抑えた、現場で選ばれるスタンダード"}
    ]
}

DEFAULTS = {
    "軽自動車": {"w": 155, "p": 65, "i": 14},
    "コンパクト": {"w": 175, "p": 65, "i": 15},
    "ミニバン": {"w": 195, "p": 65, "i": 15},
    "セダン・クーペ": {"w": 215, "p": 45, "i": 17},
    "SUV": {"w": 225, "p": 65, "i": 17},
    "バン・商用車": {"w": 195, "p": 80, "i": 15},
    "軽トラ・軽バン": {"w": 145, "p": 80, "i": 12}
}

WIDTH_OPTIONS = [135 + (i * 5) for i in range(21)]
PROFILE_OPTIONS = [35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]
INCH_OPTIONS = [12 + i for i in range(11)]

# =========================================================================
# 🔄 Google Drive CSV ローダー
# =========================================================================
def get_gdrive_direct_url(url):
    """Google Driveの共有リンクを直接ダウンロード可能なURLに変換する"""
    file_id = ""
    match1 = re.search(r"/file/d/([^/]+)/", url)
    match2 = re.search(r"/d/([^/]+)/", url)
    
    if len(url) > 20 and "/" not in url:
        file_id = url
    elif match1:
        file_id = match1.group(1)
    elif match2:
        file_id = match2.group(1)
    
    if file_id:
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

@st.cache_data(ttl=3600) # 1時間キャッシュ
def load_csv_data(gdrive_url):
    try:
        direct_url = get_gdrive_direct_url(gdrive_url)
        df = pd.read_csv(direct_url)
        df = df.fillna("")
        return df, True, ""
    except Exception as e:
        return pd.DataFrame(), False, str(e)


# =========================================================================
# 🧠 ロジック関数群
# =========================================================================
def normalize_name(name):
    if not name: return ""
    return str(name).upper().replace(" ", "").replace("　", "").replace("BS", "ブリヂストン").replace("™", "")

def is_brand_match(search_names, csv_product_name):
    norm_csv = normalize_name(csv_product_name)
    names = search_names if isinstance(search_names, list) else [search_names]
    for n in names:
        norm_master = normalize_name(n)
        if norm_master in norm_csv or norm_csv in norm_master:
            return True
    return False

def get_price_data(df, is_loaded, brand, width, profile, inch):
    exact_hit = None
    if is_loaded and not df.empty:
        norm_maker_master = normalize_name(brand["maker"])
        search_names = brand.get("searchNames", [brand["name"]])
        
        for _, row in df.iterrows():
            try:
                # ユーザーのCSV形式に合わせた列名チェック
                csv_w = int(float(row.get("width", row.get("幅", 0))))
                csv_p = int(float(row.get("profile", row.get("扁平率", 0))))
                csv_i = int(float(row.get("inch", row.get("インチ", 0))))
                
                if csv_w != width or csv_p != profile or csv_i != inch:
                    continue
            except: continue
            
            maker_col = row.get("maker", row.get("メーカー", ""))
            name_col = row.get("product_name", row.get("商品名", ""))
            
            norm_maker_csv = normalize_name(maker_col)
            if (norm_maker_csv in norm_maker_master) or (norm_maker_master in norm_maker_csv):
                if is_brand_match(search_names, name_col):
                    exact_hit = row
                    break

    if exact_hit is not None:
        # ユーザーのCSV（price_tier1_4unitsなど）または日本語カラム（4本コミコミ価格など）に対応
        def get_val(keys):
            for k in keys:
                if k in exact_hit and str(exact_hit[k]).replace('.0','').isdigit():
                    return int(float(exact_hit[k]))
            return 0
            
        t1 = get_val(["price_tier1_4units", "第１提案\n4本コミコミ価格", "①"])
        t2 = get_val(["price_tier2_4units", "第２提案\n４本コミコミ価格", "店長価格"])
        mgr = get_val(["price_manager_4units", "最終原価"])
        actual_name = exact_hit.get("product_name", exact_hit.get("商品名", brand["name"]))

        return {
            "tier1": t1, "tier2": t2, "manager": mgr,
            "actualName": actual_name, "isSimulated": False
        }
    
    # 見つからない場合のシミュレーション
    base = inch * inch * 130
    rank = brand["rank"]
    if rank == '松': t1, t2, mgr = base * 2.2, base * 2.0, base * 1.8
    elif rank == '竹': t1, t2, mgr = base * 1.6, base * 1.5, base * 1.3
    else: t1, t2, mgr = base * 1.2, base * 1.1, base * 1.0

    return {
        "tier1": round(t1 / 1000) * 1000,
        "tier2": round(t2 / 1000) * 1000,
        "manager": round(mgr / 1000) * 1000,
        "actualName": brand["name"],
        "isSimulated": True
    }

def get_ai_recommendation(current_rank, proposed_rank, idx):
    if current_rank == "松":
        if proposed_rank == "松": return {"text": "同等性能（最推奨）", "color": "#dc2626"} if idx == 0 else {"text": "同等性能（比較用）", "color": "#2563eb"}
        if proposed_rank == "竹": return {"text": "性能ダウン注意", "color": "#ea580c"}
        if proposed_rank == "梅": return {"text": "不満リスク大", "color": "#475569"}
    if current_rank == "竹":
        if proposed_rank == "松": return {"text": "性能アップ（快適）", "color": "#2563eb"}
        if proposed_rank == "竹": return {"text": "同等クラス（推奨）", "color": "#dc2626"} if idx == 1 else {"text": "同等クラス（標準）", "color": "#16a34a"}
        if proposed_rank == "梅": return {"text": "性能ダウン注意", "color": "#ea580c"}
    if current_rank == "梅":
        if proposed_rank == "松": return {"text": "大幅性能アップ", "color": "#2563eb"}
        if proposed_rank == "竹": return {"text": "性能アップ（推奨）", "color": "#dc2626"}
        if proposed_rank == "梅": return {"text": "同等クラス（上位）", "color": "#16a34a"} if idx == 0 else {"text": "同等クラス（標準）", "color": "#3b82f6"} if idx == 1 else {"text": "コスト最優先", "color": "#475569"}
    return {"text": "おすすめ", "color": "#3b82f6"}

# =========================================================================
# 🎨 UI / メイン画面
# =========================================================================

# サイドバー設定
with st.sidebar:
    st.title("⚙️ システム設定")
    
    st.subheader("Google Drive マスター連携")
    default_gdrive_url = "https://drive.google.com/file/d/1mY0iZIlqOl3dfuLXi5bxzWCkOJnkg99a/view?usp=sharing"
    gdrive_url = st.text_input("CSV共有リンクURL", value=default_gdrive_url)
    
    # 接続確認
    df_master = pd.DataFrame()
    is_csv_loaded = False
    
    if gdrive_url:
        with st.spinner("マスターデータを読み込み中..."):
            df_master, is_csv_loaded, err_msg = load_csv_data(gdrive_url)
        
        if is_csv_loaded:
            st.success(f"接続完了（{len(df_master)}件）")
        else:
            st.error(f"読込エラー: {err_msg}")
            
    st.divider()
    
    st.subheader("表示モード")
    price_mode_options = {"店頭表示": "tier1", "接客提案": "tier2", "店長決裁": "manager"}
    selected_mode_label = st.radio("価格モード切替", list(price_mode_options.keys()))
    price_mode = price_mode_options[selected_mode_label]


# メインヘッダー
st.title("🚗 Tire-Navi 2026")

# --- 入力エリア ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 車両・サイズ情報")
    category = st.selectbox("車種カテゴリ", list(BRAND_MASTER.keys()))
    
    if "prev_cat" not in st.session_state: st.session_state.prev_cat = category
    if st.session_state.prev_cat != category:
        st.session_state.prev_cat = category
        if category in DEFAULTS:
            st.session_state.w_idx = WIDTH_OPTIONS.index(DEFAULTS[category]["w"])
            st.session_state.p_idx = PROFILE_OPTIONS.index(DEFAULTS[category]["p"])
            st.session_state.i_idx = INCH_OPTIONS.index(DEFAULTS[category]["i"])
            
    if "w_idx" not in st.session_state: st.session_state.w_idx = WIDTH_OPTIONS.index(DEFAULTS[category]["w"])
    if "p_idx" not in st.session_state: st.session_state.p_idx = PROFILE_OPTIONS.index(DEFAULTS[category]["p"])
    if "i_idx" not in st.session_state: st.session_state.i_idx = INCH_OPTIONS.index(DEFAULTS[category]["i"])

    w_col, p_col, i_col = st.columns(3)
    tire_width = w_col.selectbox("タイヤ幅", WIDTH_OPTIONS, index=st.session_state.w_idx)
    tire_profile = p_col.selectbox("扁平率", PROFILE_OPTIONS, index=st.session_state.p_idx)
    tire_inch = i_col.selectbox("インチ", INCH_OPTIONS, index=st.session_state.i_idx)
    
    monthly_km = st.slider("月間平均走行距離 (km)", 300, 3000, 1000, 100)

with col2:
    st.subheader("2. 現着タイヤ状態")
    rank_options = {"プレミアム (松)": "松", "スタンダード (竹)": "竹", "ローコスト (梅)": "梅"}
    current_tire_rank_label = st.selectbox("現在装着されているタイヤのグレード", list(rank_options.keys()), index=1)
    current_tire_rank = rank_options[current_tire_rank_label]
    
    tread_depth = st.slider("最も少ない残溝 (mm)", 0.0, 8.0, 3.0, 0.1)
    years_old = st.slider("使用年数 (製造年から)", 1, 10, 4, 1)
    
    chk_col1, chk_col2 = st.columns(2)
    has_cracks = chk_col1.checkbox("ひび割れ・劣化あり", value=False)
    has_uneven_wear = chk_col2.checkbox("肩べり(偏摩耗)あり", value=False)

st.divider()

# --- 計算・診断ロジック ---
current_size_str = f"{tire_width}/{tire_profile}R{tire_inch}"
is_tread_warning = tread_depth <= 3.5
is_tread_danger = tread_depth <= 1.6

remaining_life_months = 0
if tread_depth > 1.6:
    remaining_life_months = max(0, math.floor(((tread_depth - 1.6) * 5000) / monthly_km))

# --- 診断結果表示 ---
st.subheader("📊 診断結果レポート")
diag_col1, diag_col2 = st.columns([1, 2])

with diag_col1:
    if is_tread_danger:
        st.error(f"#### 🚨 車検NG 限界到達\n法律で定められた限界(1.6mm)に達しています。")
    else:
        st.success(f"#### 車検NG(1.6mm)まで あと {remaining_life_months} ヶ月\n（走行換算: 約{remaining_life_months * monthly_km:,}km）")
        if has_uneven_wear:
            st.caption("※偏摩耗があるため寿命を短く算定しています")

with diag_col2:
    if is_tread_warning and not is_tread_danger:
        st.warning("⚠️ **残溝注意:** 3.5mm以下です。雨の日の停止距離が約1.3m伸び、追突リスクが高まっています。")
    if is_tread_danger:
        st.error("🚨 **危険:** 直ちに交換が必要です。整備不良となります。")
    if has_cracks:
        st.error("🚨 **ひび割れ危険:** ゴム劣化により内部に雨水が浸透し、バースト(破裂)の危険性が高い状態です。")
    if not has_cracks and years_old >= 4:
        st.warning("⚠️ **経年劣化注意:** ゴムが硬化し、雨の日のグリップ力が低下しています。")
    if has_uneven_wear:
        st.warning("⚠️ **偏摩耗（肩べり）:** タイヤの端が極端に減っており、本来の寿命より早く使えなくなります。")
    if not is_tread_warning and not has_cracks and years_old < 4 and not has_uneven_wear:
        st.success("✅ **良好:** 目立った危険な状態は見当たりません。引き続き定期点検をおすすめします。")

st.divider()

# --- 提案ロジックの実行 ---
all_brands = BRAND_MASTER.get(category, [])
matsus = [b for b in all_brands if b["rank"] == '松']
takes = [b for b in all_brands if b["rank"] == '竹']
umes = [b for b in all_brands if b["rank"] == '梅']

selected_brands = []
if current_tire_rank == '松':
    selected_brands = [matsus[0], matsus[1] if len(matsus)>1 else takes[0], takes[0] if len(matsus)>1 else takes[1] if len(takes)>1 else umes[0]]
elif current_tire_rank == '竹':
    selected_brands = [matsus[0], takes[0], umes[0]]
else:
    if len(umes) >= 3: selected_brands = [umes[0], umes[1], umes[2]]
    elif len(umes) >= 2 and len(takes) >= 1: selected_brands = [takes[0], umes[0], umes[1]]
    else: selected_brands = [matsus[0], takes[0], umes[0]]

valid_brands = [b for b in selected_brands if b][:3]
while len(valid_brands) < 3 and len(valid_brands) < len(all_brands):
    missing = next((b for b in all_brands if b not in valid_brands), None)
    if missing: valid_brands.append(missing)
    else: break

proposals = []
for idx, brand in enumerate(valid_brands):
    price_data = get_price_data(df_master, is_csv_loaded, brand, tire_width, tire_profile, tire_inch)
    current_price = price_data.get(price_mode, 0)
    
    effective_groove = 6.4 * 0.8 if has_uneven_wear else 6.4
    life_months = math.floor((effective_groove * brand["life"]) / monthly_km)
    cost_per_month = round(current_price / life_months) if life_months > 0 else 0
    ai_advice = get_ai_recommendation(current_tire_rank, brand["rank"], idx)
    
    proposals.append({
        **brand,
        "name": price_data["actualName"],
        "price": current_price,
        "lifeMonths": life_months,
        "costPerMonth": cost_per_month,
        "isSimulated": price_data["isSimulated"],
        "aiAdvice": ai_advice
    })

# --- 提案表示UI（1つのHTMLブロックにまとめて描画） ---
st.subheader(f"💡 【{current_size_str}】 最適タイヤ推奨プラン (4本コミコミ)")

# プログレスバー生成用のヘルパー関数
def get_progress_bar_html(label, value):
    pct = (value / 5) * 100
    return f"""
    <div style="display: flex; align-items: center; font-size: 11px; margin-bottom: 4px;">
        <span style="width: 60px; color: #475569; font-weight: bold;">{label}</span>
        <div style="flex: 1; background-color: #e2e8f0; height: 6px; border-radius: 9999px; overflow: hidden; margin: 0 8px;">
            <div style="background-color: #2563eb; height: 100%; width: {pct}%;"></div>
        </div>
        <span style="width: 15px; text-align: right; color: #334155; font-weight: bold;">{value}</span>
    </div>
    """

cards_html = ""
for idx, p in enumerate(proposals):
    header_bg = "linear-gradient(to right, #f59e0b, #fbbf24)" if idx == 0 else "#64748b" if idx == 1 else "#9a3412"
    border_col = "#fbbf24" if idx == 0 else "#cbd5e1" if idx == 1 else "#fcd34d"
    simulated_badge = f'<span style="background:#ffedd5;color:#ea580c;padding:2px 4px;border-radius:4px;font-size:10px;font-weight:bold;margin-bottom:4px;display:inline-block;">※CSV未登録(概算)</span>' if p["isSimulated"] else ""
    
    cards_html += f"""
    <div style="flex: 1; min-width: 250px; border: 2px solid {border_col}; border-radius: 12px; overflow: hidden; font-family: sans-serif; background: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); display: flex; flex-direction: column;">
        <div style="background: {header_bg}; color: white; text-align: center; font-weight: bold; padding: 6px; font-size: 14px;">
            提案 {idx + 1} （{p['rank']}クラス）
        </div>
        <div style="background: #f8fafc; border-bottom: 1px solid #e2e8f0; text-align: center; padding: 4px; font-size: 11px; font-weight: bold; color: {p['aiAdvice']['color']};">
            AI判定: {p['aiAdvice']['text']}
        </div>
        <div style="padding: 16px; flex: 1; display: flex; flex-direction: column;">
            <div style="font-size: 11px; color: #64748b; font-weight: bold;">{p['maker']}</div>
            <div style="font-size: 18px; font-weight: 900; color: #0f172a; margin-bottom: 8px; min-height: 44px; display: flex; align-items: flex-start;">{p['name']}</div>
            <div style="font-size: 12px; color: #334155; background: #f8fafc; padding: 8px; border-radius: 6px; min-height: 50px; margin-bottom: 12px; line-height: 1.4;">
                {p['desc']}
            </div>
            
            <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 12px;">
                {get_progress_bar_html('安全性', p['safety'])}
                {get_progress_bar_html('快適性', p['comfort'])}
                {get_progress_bar_html('雨の日', p['wet'])}
                {get_progress_bar_html('燃費・寿命', p['eco'])}
            </div>
            
            <div style="margin-top: auto;">
                <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px;">
                    <span style="font-size: 11px; color: #64748b; font-weight: bold;">交換費用総額</span>
                    <div style="text-align: right;">
                        {simulated_badge}<br/>
                        <span style="font-size: 24px; font-weight: 900; color: #0f172a; line-height: 1;">¥{p['price']:,}</span>
                    </div>
                </div>
                
                <div style="background: #eff6ff; padding: 10px; border-radius: 8px; border: 1px solid #dbeafe;">
                    <div style="font-size: 11px; color: #1e40af; font-weight: bold; margin-bottom: 6px;">
                        約 {p['lifeMonths'] // 12}年{p['lifeMonths'] % 12}ヶ月使用可能予測
                    </div>
                    <div style="background: white; padding: 6px 8px; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #bfdbfe;">
                        <span style="font-size: 10px; font-weight: bold; color: #1e3a8a;">ひと月あたり</span>
                        <span style="font-size: 18px; font-weight: 900; color: #2563eb;">¥{p['costPerMonth']:,}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

# 3つのカードを横並びにするラッパー (Flexbox)
final_html = f"""
<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px;">
    {cards_html}
</div>
"""

# st.writeではなくst.markdownを使用してHTMLを正しくレンダリングする
st.markdown(final_html, unsafe_allow_html=True)

st.caption("ご案内： 上記の月額コストは、お客様の走行距離をもとにタイヤが法定限界（1.6mm）に達するまでの予測使用期間で算出した参考値です。")
st.markdown("---\n**🖨️ 印刷について:** ブラウザの印刷機能（`Ctrl+P` または `Cmd+P`）を利用してください。設定で「背景のグラフィックを印刷する」にチェックを入れ、「A4・横・余白なし」に設定すると綺麗に印刷できます。")
