1. 打開dist資料夾
2. DEFINE_SETTING 先設定好路徑DIAG_PATH & REG_PATH (#為mark)
3. 打開Monitor.exe
(看到Panel channel = RX TX數量則有找到device)

--------------------------------------------------------------

Wifi連接
1. 電腦和手機要連相同熱點
2. 按下Wifi Connect (若有看到Unplug 或 Wifi connect即可)
3. 拔掉USB線，建議按下右邊的C按紐，當有看到already connect表是連線成功 (可多按幾下)

--------------------------------------------------------------
OTHER_FUNCTION (顯示於在右邊頁面 要拉開)
寫1 -------> 外部控制報點位置
寫2 -------> 自動parsing header檔文件 並取代對應文字

--------------------------------------------------------------
Build 專案檔
在cmd下	"python setup.py py2exe"
在dist資料夾下放 include 和 DEFINE_SETTING
