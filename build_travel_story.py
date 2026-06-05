from pathlib import Path
import base64
import html


ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / "assets" / "travel_story"


def data_uri(name):
    raw = (ASSET_DIR / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


images = {
    "opening": data_uri("scene-01-opening.png"),
    "stuck": data_uri("scene-02-stuck.png"),
    "cards": data_uri("scene-03-flashcards.png"),
    "dialogue": data_uri("scene-04-dialogue.png"),
    "finish": data_uri("scene-05-finish.png"),
}


html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>林安的西安推荐</title>
  <style>
    :root {{
      --ink: #17211f;
      --muted: #65706c;
      --paper: #fbfaf6;
      --warm: #d28a4b;
      --sage: #486f64;
      --blue: #426b8a;
      --line: rgba(23, 33, 31, .14);
      --card: rgba(255, 255, 255, .84);
      --shadow: 0 18px 50px rgba(32, 37, 35, .12);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
      line-height: 1.55;
    }}
    button, input {{ font: inherit; }}
    button {{
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 999px;
      padding: .7rem 1rem;
      cursor: pointer;
      transition: transform .18s ease, border-color .18s ease, background .18s ease, box-shadow .18s ease;
      min-height: 44px;
    }}
    button:hover {{ transform: translateY(-1px); border-color: rgba(72,111,100,.45); box-shadow: 0 8px 20px rgba(23,33,31,.08); }}
    button:active {{ transform: translateY(0); background: #f0eee8; }}
    button[aria-pressed="true"], .seg button.active {{ background: var(--ink); color: #fff; border-color: var(--ink); }}
    .section {{
      min-height: 100svh;
      display: grid;
      align-items: center;
      padding: clamp(32px, 7vw, 88px) clamp(18px, 6vw, 76px);
    }}
    .frame {{
      width: min(1120px, 100%);
      margin: 0 auto;
      display: grid;
      gap: clamp(18px, 3vw, 36px);
      align-items: center;
    }}
    .split {{ grid-template-columns: minmax(0, .82fr) minmax(320px, 1fr); }}
    .split.reverse {{ grid-template-columns: minmax(320px, 1fr) minmax(0, .82fr); }}
    .copy {{
      max-width: 620px;
      padding: clamp(6px, 1.4vw, 18px) 0;
    }}
    .kicker {{
      color: var(--sage);
      font-size: .86rem;
      letter-spacing: 0;
      font-weight: 800;
      margin: 0 0 .7rem;
    }}
    h1, h2 {{
      margin: 0;
      letter-spacing: 0;
      line-height: 1.08;
      text-wrap: balance;
    }}
    h1 {{ font-size: clamp(2.2rem, 7vw, 5.6rem); max-width: 11ch; }}
    h2 {{ font-size: clamp(1.7rem, 4vw, 3.4rem); max-width: 13ch; }}
    p {{ margin: .7rem 0 0; color: var(--muted); }}
    .scene-img {{
      width: 100%;
      max-height: 58svh;
      object-fit: contain;
      display: block;
      border-radius: 8px;
      box-shadow: var(--shadow);
      background: #fff;
    }}
    .hero-img {{ max-height: 66svh; }}
    .line {{
      display: inline-flex;
      flex-direction: column;
      gap: .18rem;
      max-width: 100%;
      margin-top: 1rem;
      padding: .9rem 1rem;
      border: 1px solid var(--line);
      background: rgba(255,255,255,.76);
      border-radius: 8px;
    }}
    .zh {{
      font-size: clamp(1.2rem, 2.6vw, 2rem);
      font-weight: 850;
      line-height: 1.3;
      white-space: normal;
      word-break: keep-all;
      overflow-wrap: anywhere;
    }}
    .py {{ color: var(--sage); font-weight: 750; }}
    .en {{
      display: none;
      color: var(--blue);
      border-top: 1px solid var(--line);
      margin-top: .5rem;
      padding-top: .5rem;
    }}
    .line.open .en {{ display: block; }}
    .tiny {{
      font-size: .88rem;
      color: var(--muted);
    }}
    .dialogue {{
      display: grid;
      gap: 1rem;
      margin-top: 1rem;
      max-width: 650px;
    }}
    .bubble {{
      width: fit-content;
      max-width: min(590px, 100%);
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: .92rem 1rem;
      box-shadow: 0 10px 26px rgba(23,33,31,.06);
    }}
    .bubble.right {{ justify-self: end; background: #f7fbf8; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(4, minmax(150px, 1fr));
      gap: .9rem;
      margin-top: 1.2rem;
    }}
    .flip {{
      min-height: 164px;
      perspective: 1000px;
      border: 0;
      padding: 0;
      background: transparent;
      text-align: left;
    }}
    .flip-inner {{
      position: relative;
      width: 100%;
      min-height: 164px;
      transform-style: preserve-3d;
      transition: transform .45s ease;
    }}
    .flip[aria-pressed="true"] .flip-inner {{ transform: rotateY(180deg); }}
    .face {{
      position: absolute;
      inset: 0;
      backface-visibility: hidden;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 1rem;
      box-shadow: 0 12px 28px rgba(23,33,31,.07);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      overflow: hidden;
    }}
    .back {{ transform: rotateY(180deg); background: #fffaf1; }}
    .word {{ font-size: 1.42rem; font-weight: 900; word-break: keep-all; }}
    .pair {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-top: 1.1rem;
    }}
    .grammar-card, .tone-card, .practice-card {{
      border: 1px solid var(--line);
      background: var(--card);
      border-radius: 8px;
      padding: clamp(1rem, 2vw, 1.35rem);
      box-shadow: 0 12px 32px rgba(23,33,31,.07);
    }}
    .rule {{
      color: var(--ink);
      font-weight: 780;
      margin-top: .8rem;
    }}
    .tone-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(260px, 1fr));
      gap: 1rem;
      margin-top: 1.1rem;
    }}
    .tone-head {{
      display: flex;
      justify-content: space-between;
      gap: .8rem;
      align-items: flex-start;
    }}
    .tone-title {{ font-size: 1.05rem; font-weight: 900; word-break: keep-all; overflow-wrap: anywhere; }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: .55rem;
      align-items: center;
      margin-top: .8rem;
    }}
    .seg {{
      display: inline-flex;
      padding: .18rem;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
    }}
    .seg button {{
      border: 0;
      min-height: 36px;
      padding: .42rem .72rem;
      box-shadow: none;
    }}
    .rate {{
      display: inline-flex;
      align-items: center;
      gap: .55rem;
      color: var(--muted);
      font-size: .9rem;
    }}
    .rate input {{ width: 116px; accent-color: var(--sage); }}
    .tone-svg {{
      width: 100%;
      height: 146px;
      margin-top: .8rem;
      background: linear-gradient(180deg, rgba(255,255,255,.8), rgba(255,255,255,.35));
      border-radius: 8px;
      border: 1px solid rgba(23,33,31,.08);
    }}
    .syllables {{
      display: grid;
      gap: .35rem;
      margin-top: .55rem;
      color: var(--muted);
      font-size: .86rem;
    }}
    .syll-row {{
      display: flex;
      gap: .38rem;
      flex-wrap: wrap;
      align-items: center;
    }}
    .pill {{
      display: inline-flex;
      padding: .18rem .45rem;
      border-radius: 999px;
      background: rgba(72,111,100,.1);
      color: var(--sage);
      font-weight: 760;
    }}
    .voice-missing {{
      display: none;
      color: var(--muted);
      font-size: .9rem;
      margin-top: .6rem;
    }}
    .practice {{
      display: grid;
      grid-template-columns: repeat(3, minmax(190px, 1fr));
      gap: 1rem;
      margin-top: 1.1rem;
    }}
    .practice-card h3 {{
      margin: 0 0 .6rem;
      font-size: 1.05rem;
    }}
    .practice-card .line {{ margin-top: .6rem; width: 100%; }}
    .end-band {{
      display: grid;
      gap: 1.2rem;
      justify-items: start;
    }}
    @media (max-width: 900px) {{
      .split, .split.reverse, .pair {{ grid-template-columns: 1fr; }}
      .reverse .copy {{ order: 1; }}
      .reverse .scene-img {{ order: 2; }}
      .cards, .tone-grid, .practice {{ grid-template-columns: 1fr; }}
      .section {{ min-height: auto; padding-top: 58px; padding-bottom: 58px; }}
      .scene-img, .hero-img {{ max-height: none; }}
      .zh {{ font-size: 1.25rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="section">
      <div class="frame split">
        <div class="copy">
          <p class="kicker">星期五上午，上海</p>
          <h1>林安要把西安说清楚。</h1>
          <p>28 岁的市场协调员林安，要给第一次来中国的同事 Alex 推荐一个周末旅行地。她选了西安。</p>
          <div class="line core" role="button" tabindex="0">
            <span class="zh">我请你当我的导游。</span>
            <span class="py">Wǒ qǐng nǐ / dāng wǒ de dǎoyóu.</span>
            <span class="en">I invite you to be my guide.</span>
            <span class="tiny">点击显示英文</span>
          </div>
        </div>
        <img class="scene-img hero-img" src="{images['opening']}" alt="林安在办公室准备西安旅行推荐" />
      </div>
    </section>

    <section class="section">
      <div class="frame split reverse">
        <img class="scene-img" src="{images['stuck']}" alt="林安听同事问西安旅行时卡住" />
        <div class="copy">
          <p class="kicker">第一句，她听懂了；第二句，她卡住了</p>
          <h2>Alex 想知道，不只是兵马俑。</h2>
          <div class="dialogue">
            <div class="bubble">
              <div class="line core" role="button" tabindex="0">
                <span class="zh">你去过西安吗？</span>
                <span class="py">Nǐ qù guo / Xī'ān ma?</span>
                <span class="en">Have you been to Xi'an?</span>
                <span class="tiny">点击显示英文</span>
              </div>
            </div>
            <div class="bubble right">
              <div class="line core" role="button" tabindex="0">
                <span class="zh">除了兵马俑以外，西安还有什么好玩儿的地方？</span>
                <span class="py">Chúle Bīngmáyǒng yǐwài / Xī'ān hái yǒu shénme / hǎowánr de dìfang?</span>
                <span class="en">Besides the Terracotta Warriors, what other fun places does Xi'an have?</span>
                <span class="tiny">点击显示英文</span>
              </div>
            </div>
          </div>
          <p class="rule">林安需要的不只是词，是能把“还有什么”自然接下去的一口气。</p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="frame">
        <div class="copy">
          <p class="kicker">她先把旅行这件事拆成可说的小块</p>
          <h2>一张词卡，解决一个当下的问题。</h2>
        </div>
        <img class="scene-img" src="{images['cards']}" alt="林安用空白词卡练习旅行中文词语" />
        <div class="cards" aria-label="旅行词卡">
          {''.join([
            f'''<button class="flip" aria-pressed="false"><span class="flip-inner"><span class="face front"><span><span class="word">{w}</span><br><span class="py">{p}</span></span><span class="tiny">点击翻面</span></span><span class="face back"><span><strong>{m}</strong><br>{c}</span><span class="tiny">{e}</span></span></span></button>'''
            for w, p, m, c, e in [
              ("导游", "dǎoyóu", "guide", "当导游、找导游", "我请你当我的导游。"),
              ("名胜古迹", "míngshèng gǔjì", "historic places", "很多名胜古迹", "西安有很多名胜古迹。"),
              ("小吃", "xiǎochī", "local snacks", "有名的小吃", "西安的小吃很有名。"),
              ("特产", "tèchǎn", "local specialty", "当地特产", "这是我们那儿的特产。"),
              ("好玩儿", "hǎowánr", "fun", "好玩儿的地方", "那个地方很好玩儿。"),
              ("可惜", "kěxī", "what a pity", "真可惜、太可惜", "我没去华清池，真可惜。"),
              ("机会", "jīhuì", "chance", "有机会", "以后有机会我一定去。"),
              ("等于", "děngyú", "just like", "等于没去", "不练习等于没学。"),
            ]
          ])}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="frame split">
        <div class="copy">
          <p class="kicker">中午，她重新开口</p>
          <h2>规则藏在对话里。</h2>
          <div class="dialogue">
            <div class="bubble">
              <div class="line core" role="button" tabindex="0">
                <span class="zh">除了兵马俑以外，西安还有华清池和大雁塔。</span>
                <span class="py">Chúle Bīngmáyǒng yǐwài / Xī'ān hái yǒu Huáqīngchí hé Dàyàntǎ.</span>
                <span class="en">Besides the Terracotta Warriors, Xi'an also has Huaqing Pool and the Big Wild Goose Pagoda.</span>
                <span class="tiny">点击显示英文</span>
              </div>
            </div>
            <div class="bubble right">
              <div class="line core" role="button" tabindex="0">
                <span class="zh">西安有很多小吃，比如凉皮、肉夹馍。</span>
                <span class="py">Xī'ān yǒu hěn duō xiǎochī / bǐrú liángpí, ròujiāmó.</span>
                <span class="en">Xi'an has many snacks, for example liangpi and roujiamo.</span>
                <span class="tiny">点击显示英文</span>
              </div>
            </div>
            <div class="bubble">
              <div class="line core" role="button" tabindex="0">
                <span class="zh">没看过兵马俑，等于没去过西安。</span>
                <span class="py">Méi kàn guo Bīngmáyǒng / děngyú / méi qù guo Xī'ān.</span>
                <span class="en">If you haven't seen the Terracotta Warriors, it's like you haven't been to Xi'an.</span>
                <span class="tiny">点击显示英文</span>
              </div>
            </div>
          </div>
          <p class="rule">先说一个已经知道的，再用“还”加别的；“比如”后面放例子；“等于”把遗憾说得更有力。</p>
        </div>
        <img class="scene-img" src="{images['dialogue']}" alt="林安在会议室和同事练习旅行推荐对话" />
      </div>
    </section>

    <section class="section">
      <div class="frame">
        <div class="copy">
          <p class="kicker">下午四点，她开始修声音</p>
          <h2>同一句话，逐字像走路，连读像真的在说话。</h2>
          <p id="voiceStatus" class="voice-missing">这台设备没有找到中文语音，可看曲线跟读。</p>
        </div>
        <div id="toneGrid" class="tone-grid"></div>
      </div>
    </section>

    <section class="section">
      <div class="frame split reverse">
        <img class="scene-img" src="{images['finish']}" alt="林安成功发送西安旅行语音推荐" />
        <div class="copy end-band">
          <div>
            <p class="kicker">傍晚，她把语音发出去了</p>
            <h2>Alex 听懂了，也想去了。</h2>
          </div>
          <div class="line core" role="button" tabindex="0">
            <span class="zh">我去过西安，那儿有很多名胜古迹，也有很多有特色的小吃。除了兵马俑以外，西安还有华清池和大雁塔。兵马俑我当然看了，可惜华清池没去。以后有机会，我一定再去。</span>
            <span class="py">Wǒ qù guo Xī'ān / nàr yǒu hěn duō míngshèng gǔjì / yě yǒu hěn duō yǒu tèsè de xiǎochī. Chúle Bīngmáyǒng yǐwài / Xī'ān hái yǒu Huáqīngchí hé Dàyàntǎ. Bīngmáyǒng wǒ dāngrán kàn le / kěxī Huáqīngchí méi qù. Yǐhòu yǒu jīhuì / wǒ yídìng zài qù.</span>
            <span class="en">I have been to Xi'an. It has many historic places and many special local snacks. Besides the Terracotta Warriors, Xi'an also has Huaqing Pool and the Big Wild Goose Pagoda. Of course I saw the Terracotta Warriors, but unfortunately I didn't go to Huaqing Pool. If I have the chance later, I will definitely go again.</span>
            <span class="tiny">点击显示英文</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="frame">
        <div class="copy">
          <p class="kicker">把这件事说出来</p>
          <h2>先替林安说，再替自己说。</h2>
        </div>
        <div class="practice">
          <div class="practice-card">
            <h3>短句</h3>
            <div class="line core" role="button" tabindex="0"><span class="zh">我去过西安。</span><span class="py">Wǒ qù guo Xī'ān.</span><span class="en">I have been to Xi'an.</span><span class="tiny">点击显示英文</span></div>
            <div class="line core" role="button" tabindex="0"><span class="zh">那儿有很多名胜古迹。</span><span class="py">Nàr yǒu hěn duō míngshèng gǔjì.</span><span class="en">There are many historic places there.</span><span class="tiny">点击显示英文</span></div>
          </div>
          <div class="practice-card">
            <h3>完整句</h3>
            <div class="line core" role="button" tabindex="0"><span class="zh">除了北京以外，我还想去西安。</span><span class="py">Chúle Běijīng yǐwài / wǒ hái xiǎng qù Xī'ān.</span><span class="en">Besides Beijing, I also want to go to Xi'an.</span><span class="tiny">点击显示英文</span></div>
            <div class="line core" role="button" tabindex="0"><span class="zh">没吃过小吃等于没来过这儿。</span><span class="py">Méi chī guo xiǎochī / děngyú méi lái guo zhèr.</span><span class="en">If you haven't tried the snacks, it's like you haven't come here.</span><span class="tiny">点击显示英文</span></div>
          </div>
          <div class="practice-card">
            <h3>自然小段</h3>
            <div class="line core" role="button" tabindex="0"><span class="zh">我想推荐一个旅行的好地方。那儿有很多名胜古迹，比如……。除了……以外，还……。可惜……。以后有机会，我一定……。</span><span class="py">Wǒ xiǎng tuījiàn yí ge lǚxíng de hǎo dìfang. Nàr yǒu hěn duō míngshèng gǔjì, bǐrú... Chúle... yǐwài, hái... Kěxī... Yǐhòu yǒu jīhuì, wǒ yídìng...</span><span class="en">I want to recommend a good place to travel. There are many historic places there, for example... Besides..., there is also... Unfortunately... If I have the chance later, I will definitely...</span><span class="tiny">点击显示英文</span></div>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    const toneCards = [
      {{
        zh: "你去过西安吗？",
        py: "nǐ qù guo / Xī'ān ma",
        note: "“你”在四声前读半三声；“吗”轻短，句尾轻轻上扬。",
        natural: [
          ["nǐ", "half3", "○"], ["qù", "4", "●"], ["guo", "0", "○"], ["/", "break", ""], ["Xī", "1", "●"], ["ān", "1", "●"], ["ma", "0", "○"]
        ],
        word: [
          ["nǐ", "3", "○"], ["qù", "4", "●"], ["guo", "0", "○"], ["/", "break", ""], ["Xī", "1", "●"], ["ān", "1", "●"], ["ma", "0", "○"]
        ]
      }},
      {{
        zh: "那儿有很多名胜古迹。",
        py: "nàr / yóu hěn duō / míngshèng gǔjì",
        note: "“有很”三声连读，前字变二声；“很”和“古”在后字前读半三声。",
        natural: [
          ["nàr", "4", "●"], ["/", "break", ""], ["yóu", "2", "○"], ["hěn", "half3", "●"], ["duō", "1", "○"], ["/", "break", ""], ["míng", "2", "●"], ["shèng", "4", "●"], ["gǔ", "half3", "●"], ["jì", "4", "●"]
        ],
        word: [
          ["nàr", "4", "●"], ["/", "break", ""], ["yǒu", "3", "○"], ["hěn", "3", "●"], ["duō", "1", "○"], ["/", "break", ""], ["míng", "2", "●"], ["shèng", "4", "●"], ["gǔ", "3", "●"], ["jì", "4", "●"]
        ]
      }},
      {{
        zh: "没看过兵马俑，等于没去过西安。",
        py: "méi kàn guo Bīng-má-yǒng / děngyú / méi qù guo Xī'ān",
        note: "“马俑”两个三声相连，“马”变二声；“等”在二声前读半三声。",
        natural: [
          ["méi", "2", "○"], ["kàn", "4", "●"], ["guo", "0", "○"], ["Bīng", "1", "●"], ["má", "2", "●"], ["yǒng", "3", "●"], ["/", "break", ""], ["děng", "half3", "●"], ["yú", "2", "○"], ["/", "break", ""], ["méi", "2", "○"], ["qù", "4", "●"], ["guo", "0", "○"], ["Xī", "1", "●"], ["ān", "1", "●"]
        ],
        word: [
          ["méi", "2", "○"], ["kàn", "4", "●"], ["guo", "0", "○"], ["Bīng", "1", "●"], ["mǎ", "3", "●"], ["yǒng", "3", "●"], ["/", "break", ""], ["děng", "3", "●"], ["yú", "2", "○"], ["/", "break", ""], ["méi", "2", "○"], ["qù", "4", "●"], ["guo", "0", "○"], ["Xī", "1", "●"], ["ān", "1", "●"]
        ]
      }},
      {{
        zh: "除了兵马俑以外，西安还有什么好玩儿的地方？",
        py: "chúle Bīng-má-yǒng yǐwài / Xī'ān hái yǒu shénme / hǎowánr de dìfang",
        note: "“兵马俑”里“马”变二声；“以”和“好”都读半三声，长句按三块说。",
        natural: [
          ["chú", "2", "○"], ["le", "0", "○"], ["Bīng", "1", "●"], ["má", "2", "●"], ["yǒng", "3", "●"], ["yǐ", "half3", "○"], ["wài", "4", "○"], ["/", "break", ""], ["Xī", "1", "●"], ["ān", "1", "●"], ["hái", "2", "○"], ["yǒu", "3", "●"], ["shén", "2", "○"], ["me", "0", "○"], ["/", "break", ""], ["hǎo", "half3", "●"], ["wánr", "2", "○"], ["de", "0", "○"], ["dì", "4", "●"], ["fang", "0", "○"]
        ],
        word: [
          ["chú", "2", "○"], ["le", "0", "○"], ["Bīng", "1", "●"], ["mǎ", "3", "●"], ["yǒng", "3", "●"], ["yǐ", "3", "○"], ["wài", "4", "○"], ["/", "break", ""], ["Xī", "1", "●"], ["ān", "1", "●"], ["hái", "2", "○"], ["yǒu", "3", "●"], ["shén", "2", "○"], ["me", "0", "○"], ["/", "break", ""], ["hǎo", "3", "●"], ["wánr", "2", "○"], ["de", "0", "○"], ["dì", "4", "●"], ["fang", "0", "○"]
        ]
      }},
      {{
        zh: "我请你当我的导游。",
        py: "wó qíng nǐ / dāng wǒ de dǎoyóu",
        note: "“我请你”三个三声连读，前两个变二声，最后一个读半三声；“导”也读半三声。",
        natural: [
          ["wó", "2", "○"], ["qíng", "2", "●"], ["nǐ", "half3", "○"], ["/", "break", ""], ["dāng", "1", "●"], ["wǒ", "3", "○"], ["de", "0", "○"], ["dǎo", "half3", "●"], ["yóu", "2", "○"]
        ],
        word: [
          ["wǒ", "3", "○"], ["qǐng", "3", "●"], ["nǐ", "3", "○"], ["/", "break", ""], ["dāng", "1", "●"], ["wǒ", "3", "○"], ["de", "0", "○"], ["dǎo", "3", "●"], ["yóu", "2", "○"]
        ]
      }}
    ];

    function toneY(tone, i) {{
      const maps = {{
        "1": [[18, 18]],
        "2": [[62, 24]],
        "4": [[24, 74]],
        "0": [[48, 48]],
        "half3": [[58, 74]],
        "3": [[66, 76, 50]]
      }};
      return maps[tone] || maps["0"];
    }}

    function pathForTone(tone, x, w) {{
      const y = toneY(tone)[0];
      if (tone === "3") return `M ${{x + 6}} ${{y[0]}} Q ${{x + w * .5}} ${{y[1]}} ${{x + w - 6}} ${{y[2]}}`;
      if (tone === "0") return `M ${{x + w * .36}} ${{y[0]}} L ${{x + w * .64}} ${{y[1]}}`;
      return `M ${{x + 6}} ${{y[0]}} L ${{x + w - 6}} ${{y[1]}}`;
    }}

    function renderSvg(card, mode, svg) {{
      const data = card[mode];
      const units = data.filter(d => d[1] !== "break").length;
      const width = Math.max(620, units * (mode === "natural" ? 58 : 70));
      svg.setAttribute("viewBox", `0 0 ${{width}} 146`);
      let x = 16;
      let out = `<line x1="12" y1="86" x2="${{width - 12}}" y2="86" stroke="rgba(23,33,31,.12)" stroke-dasharray="4 8"/>`;
      data.forEach(d => {{
        if (d[1] === "break") {{
          out += `<text x="${{x + 6}}" y="106" fill="#65706c" font-size="21" font-weight="800">/</text>`;
          x += mode === "natural" ? 32 : 44;
          return;
        }}
        const w = mode === "natural" ? 54 : 66;
        const color = d[2] === "●" ? "#c36b32" : "#486f64";
        out += `<path d="${{pathForTone(d[1], x, w)}}" stroke="${{color}}" stroke-width="4" fill="none" stroke-linecap="round"/>`;
        out += `<text x="${{x + w / 2}}" y="112" text-anchor="middle" fill="#17211f" font-size="14" font-weight="760">${{d[0]}}</text>`;
        out += `<text x="${{x + w / 2}}" y="134" text-anchor="middle" fill="${{color}}" font-size="14" font-weight="900">${{d[2]}}</text>`;
        x += w;
      }});
      svg.innerHTML = out;
    }}

    function speak(text, rate, mode) {{
      if (!("speechSynthesis" in window)) return;
      speechSynthesis.cancel();
      if (mode === "word") {{
        const chars = Array.from(text.replace(/[，。？]/g, " "));
        let delay = 0;
        chars.forEach(ch => {{
          if (ch.trim()) {{
            setTimeout(() => {{
              const u = new SpeechSynthesisUtterance(ch);
              u.lang = "zh-CN";
              u.rate = Math.min(.72, rate);
              speechSynthesis.speak(u);
            }}, delay);
            delay += 540 / Math.max(rate, .5);
          }}
        }});
      }} else {{
        const u = new SpeechSynthesisUtterance(text);
        u.lang = "zh-CN";
        u.rate = rate;
        speechSynthesis.speak(u);
      }}
    }}

    function hasChineseVoice() {{
      if (!("speechSynthesis" in window)) return false;
      return speechSynthesis.getVoices().some(v => /zh|Chinese|Mandarin/i.test(v.lang + " " + v.name));
    }}

    function buildToneCards() {{
      const grid = document.getElementById("toneGrid");
      grid.innerHTML = "";
      toneCards.forEach((card, idx) => {{
        const el = document.createElement("article");
        el.className = "tone-card";
        el.innerHTML = `
          <div class="tone-head">
            <div>
              <div class="tone-title">${{card.zh}}</div>
              <div class="py">${{card.py}}</div>
            </div>
            <button class="speak">朗读</button>
          </div>
          <div class="controls">
            <span class="seg">
              <button class="mode active" data-mode="natural">连读</button>
              <button class="mode" data-mode="word">逐字</button>
            </span>
            <label class="rate">速度 <input type="range" min="0.5" max="1" step="0.05" value="0.78"></label>
          </div>
          <svg class="tone-svg" role="img" aria-label="音高曲线"></svg>
          <div class="syllables">
            <div class="syll-row natural-row"></div>
            <div class="tiny">${{card.note}}</div>
          </div>`;
        const svg = el.querySelector("svg");
        const row = el.querySelector(".natural-row");
        let mode = "natural";
        function refresh() {{
          renderSvg(card, mode, svg);
          row.innerHTML = card[mode].map(d => d[1] === "break" ? `<span class="pill">/</span>` : `<span>${{d[0]}} ${{d[2]}}</span>`).join("");
          el.querySelectorAll(".mode").forEach(b => b.classList.toggle("active", b.dataset.mode === mode));
        }}
        el.querySelectorAll(".mode").forEach(btn => btn.addEventListener("click", () => {{ mode = btn.dataset.mode; refresh(); }}));
        el.querySelector(".speak").addEventListener("click", () => speak(card.zh, Number(el.querySelector("input").value), mode));
        refresh();
        grid.appendChild(el);
      }});
      const ok = hasChineseVoice();
      document.querySelectorAll(".speak").forEach(btn => btn.style.display = ok ? "" : "none");
      document.getElementById("voiceStatus").style.display = ok ? "none" : "block";
    }}

    document.querySelectorAll(".core").forEach(el => {{
      el.addEventListener("click", () => el.classList.toggle("open"));
      el.addEventListener("keydown", e => {{
        if (e.key === "Enter" || e.key === " ") {{ e.preventDefault(); el.classList.toggle("open"); }}
      }});
    }});
    document.querySelectorAll(".flip").forEach(card => {{
      card.addEventListener("click", () => card.setAttribute("aria-pressed", card.getAttribute("aria-pressed") !== "true"));
    }});
    buildToneCards();
    if ("speechSynthesis" in window) speechSynthesis.onvoiceschanged = buildToneCards;
  </script>
</body>
</html>
"""

(ROOT / "travel_story_lesson.html").write_text(html_doc, encoding="utf-8")
print(ROOT / "travel_story_lesson.html")
