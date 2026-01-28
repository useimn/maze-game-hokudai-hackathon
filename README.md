# maze-game-hokudai-hackathon
北大内で優勝した、PythonとProcessingで作成した迷路ゲーム

Late For School (遅刻寸前！通学サバイバル)
大学の授業に間に合わせるため、自宅（作成者のおおよその位置）から、数々の障害を乗り越えて大学を目指す、スリル満点のトップダウン型迷路アクションゲームです。

🎓 ゲーム概要
「一限」「三限」「夜の集中講義」……。学生を待ち受けるのは、単なる道迷いだけではありません。空腹、激しい交通量、照りつける太陽、うるさい蚊。無事にゴールに辿り着けなければ、教授への謝罪メール（Apology Email）を書く羽目になります。

🕹 モード紹介
3つの時間帯ごとに異なるギミックが用意されています。

1st Period (1限):

交通量が多く、車を避ける必要があります。

学内の「おにぎり」をすべて回収しないと、校門（ゲート）が開きません。
<img width="1790" height="929" alt="image" src="https://github.com/user-attachments/assets/2117ea7e-5970-4262-878e-c4be2016cae7" />

<img width="1796" height="929" alt="image" src="https://github.com/user-attachments/assets/6d73ad9c-35ba-4bb6-88ef-879391a2a6df" />

<img width="1779" height="934" alt="image" src="https://github.com/user-attachments/assets/41e562e9-2b05-44dd-8d3f-58a3922f74d1" />



3rd Period (3限):

強烈な日差し（太陽）が追いかけてきます。

捕まると熱中症でフリーズするため、water とタイピングして回復してください。
<img width="1809" height="937" alt="image" src="https://github.com/user-attachments/assets/c4ec1203-6f88-465e-9461-9418cc78cdde" />

Night (夜間):

視界が悪く、懐中電灯（Flashlight）を拾うと色が反転し、隠れた子供が見えるようになります。

捕まったら rescue と入力して脱出しましょう。
<img width="1775" height="909" alt="image" src="https://github.com/user-attachments/assets/36419bd5-3294-4d98-aa49-61aaa034a716" />

<img width="1775" height="922" alt="image" src="https://github.com/user-attachments/assets/3167d98c-edc2-425d-8e02-4308588bc7f2" />



🛠 特徴的なギミック
自転車（Bicycle）: 拾うと移動スピードが大幅にアップします。

スリップゾーン: 床が凍っているエリアでは慣性が働き、制御が難しくなります。

蚊: 突然襲ってくる紫色の蚊。捕まったら k キーを連打してデバッグ（脱出）してください。

謝罪メール生成: タイムアップになると、受講している授業の教授に合わせて、誠意ある（？）謝罪メールが自動生成されます。

🎮 操作方法
移動: 矢印キー (↑, ↓, ←, →)

状態解除:

タイピング: water または rescue

連打: k キー

メニューに戻る: 画面をクリック（リザルト/謝罪画面時）

🚀 実行方法
Processing をインストール。

Python Mode を追加。

late_for_school.py (本ファイル) を実行。

💡 技術的なポイント (Tech Stack)
Language: Python (Processing Python Mode)

Concepts:

OOP (オブジェクト指向): 障害物、車、アイテムなどをクラス化して管理。

衝突判定: 円形および矩形の衝突アルゴリズムの実装。

座標計算: 線分との距離計算を用いた「道（Path）」の判定ロジック。
　本ゲームでは、プレイヤーが「道」の上にいるかどうかを判定するために、点と線分の距離計算を用いたアルゴリズムを実装しています。
 1. 数学的背景2点 $(x_1, y_1), (x_2, y_2)$ を通る直線の方程式は、一般形 $Ax + By + C = 0$ で表されます。ここで、各係数は以下の通りです。$A = y_1 - y_2$$B = x_2 - x_1$$C = x_1 y_2 - x_2 y_1$ある点 $(x_0, y_0)$ からこの直線までの距離 $d$ は、以下の公式で求められます。$$d = \frac{|Ax_0 + By_0 + C|}{\sqrt{A^2 + B^2}}$$
  2. アルゴリズムの実装単なる直線ではなく「線分（Segment）」として判定するため、以下の2段階のチェックを行っています。
距離チェック: 公式を用いて計算した距離 $d$ が、道幅 path_width の半分以下であるか。
範囲チェック（Bounding Box）: プレイヤーの座標が、線分の始点と終点が作る矩形範囲内（プラス遊び分）に収まっているか。
この実装のメリット柔軟なコース設計: 座標のリストを渡すだけで、斜めの道やクランクのような複雑な形状の道を簡単に定義できます。実際の自宅付近（札幌市東区北13条東付近）から北大までの道）
<img width="1596" height="719" alt="image" src="https://github.com/user-attachments/assets/eff90d40-9e6b-4864-b731-9eabe930a051" />
3．計算の軽量化: 矩形（Bounding Box）による範囲チェックを事前に行うことで、不要な計算を抑え、リアルタイムな判定を実現しています。

状態管理: MENU, PLAYING, APOLOGY_SCREEN などのステートマシンによる遷移。

Author
Yusei Mine - [Hokkaido University]
