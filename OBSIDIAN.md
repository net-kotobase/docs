# Markdownを手放さず、Obsidian vaultを「問い合わせ可能な記憶」にする

Obsidianの良さは、Markdownが手元に残ることです。Kotobaseはその所有権を
変えません。vaultを独自形式へ移行せず、Markdown本文・frontmatter・
`[[wikilink]]` をportableなdatomへ変換し、複数ノートをまたぐ問いを
Datalog、SPARQL、Cypher、GraphQLから実行できます。

つまり、Obsidianはこれまで通り書く場所のままです。Kotobaseはその外側に、
ノート間の関係を安全に同期・検索・再利用するgraph layerを加えます。
クラウドへ移行するためにvaultを捨てる必要も、AIへvault全体を渡す必要も
ありません。

向いている用途:

- 「このプロジェクトに関係する人物・決定・未解決事項」をリンクの深さを
  越えて探す
- AI agentへvault全体を渡さず、必要な関係だけqueryして渡す
- 複数端末やagentから更新しても、競合を黙って上書きせず両方を残す
- ある時点の知識グラフをCIDで固定し、後から同じ根拠を再現する
- ObsidianをやめてもMarkdown原本とexportしたEDNをそのまま保持する

## 1. ローカルで変換する

```sh
kbb --backend sci scripts/edn-datomize.cljk obsidian-vault ~/Documents/MyVault ./out/obsidian
```

`out/obsidian/vault.edn` と `schema.edn` が生成されます。変換はローカルで
完結し、hidden directoryを読みません。添付ファイル、plugin設定、credential
は送信しません。frontmatterはv1ではlosslessなEDN文字列として保持します。

## 2. 自分のtenant graphへ書く

```python
from pathlib import Path
from kotobase import Client
from kotobase_auth import Keypair

kb = Client(base="https://kotobase-cf-wasm-testnet.aozora.app")
identity = Keypair()  # 永続利用ではseedを安全に保管して再利用
tx = Path("out/obsidian/vault.edn").read_text()
receipt = kb.transact(identity, "obsidian", tx)
print(receipt["graph"], receipt["commit"])
```

target graphは署名したDIDと`db_name`からserver側で導出されるため、clientが
別tenantのgraphを指定することはできません。

## 3. Obsidian pluginで双方向同期する

`integrations/obsidian-kotobase` をbuildし、生成された`main.js`、
`manifest.json`、`README.md`をvaultの
`.obsidian/plugins/kotobase-sync/`へ配置します。

```sh
cd integrations/obsidian-kotobase
npm ci
npm run build
```

pluginにはpush、pull、双方向syncのcommandと、Markdownの作成・変更・削除・rename後のdebounced syncが
あります。同期済みhashを共通祖先として比較し、localとremoteが両方変更された
場合は上書きせず、remote版を`.kotobase-conflicts/<time>/...`へ保存します。
target graphは初回pushのresponseから記録し、以後のpullで使用します。
frontmatterは本文とは別のlossless文字列としても保持します。remote datomが履歴を
含む場合はtransaction順にretractionを反映し、`..`、absolute path、`.obsidian/`
などvault外・設定領域へ書けるpathは受け付けません。

現在の境界: 添付ファイル、Obsidian plugin設定そのもの、canvasは同期しません。
Bearer tokenはObsidianのplugin dataへ保存されるため、共有端末では専用profileと
Kotobaseの`editor` service accountを使い、permissionを`data:read`と`data:write`だけに
絞って定期rotateしてください。最初に生成EDNを確認できるone-shot importも、監査・
移行用として引き続き提供します。
