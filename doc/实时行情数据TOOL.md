����Ӣ������Stock_spot_quotations
������������ʵʱ��������

identity:
  author: shaoxing_xie
  name: Stock_spot_quotations
  label:
    zh_Hans: ʵʱ��������
    en_US: Stock spot quotations 
description:���η���ָ����Ʊ�г��������й�˾��ʵʱ�������ݣ�����A�ɡ��۹ɡ����ɵȡ�

parameters:
  - name: interface
    type: select
    required: true
    form: llm
    default: stock_zh_a_spot_em
    description: �ӿ�����
    llm_description: ͨ��AKShare��װ�����ݽӿڣ���ȡָ����Ʊ�г��������й�˾��ʵʱ��������
    human_description:ͨ��AKShare��װ�����ݽӿڣ���ȡָ����Ʊ�г��������й�˾��ʵʱ��������
    label:
      en_US: Interface
      zh_Hans: �ӿ�����

1���ӿ�: stock_sh_a_spot_em
�ӿ��������������Ƹ���-��A��-ʵʱ��������

Ŀ���ַ: http://quote.eastmoney.com/center/gridlist.html#sh_a_board

����: �����Ƹ���-�� A ��-ʵʱ��������

����: ���η������л� A �����й�˾��ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()
print(stock_sh_a_spot_em_df)
```

2���ӿ�: stock_sz_a_spot_em
�ӿ��������������Ƹ���-��A��-ʵʱ��������

Ŀ���ַ: http://quote.eastmoney.com/center/gridlist.html#sz_a_board

����: �����Ƹ���-�� A ��-ʵʱ��������

����: ���η��������� A �����й�˾��ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_sz_a_spot_em_df = ak.stock_sz_a_spot_em()
print(stock_sz_a_spot_em_df)
```

3���ӿ�: stock_bj_a_spot_em
�ӿ��������������Ƹ���-��A��-ʵʱ��������

Ŀ���ַ: http://quote.eastmoney.com/center/gridlist.html#bj_a_board

����: �����Ƹ���-�� A ��-ʵʱ��������

����: ���η������о� A �����й�˾��ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_bj_a_spot_em_df = ak.stock_bj_a_spot_em()
print(stock_bj_a_spot_em_df)
```

4���ӿ�: stock_new_a_spot_em
�ӿ��������������Ƹ���-�¹�-ʵʱ��������

Ŀ���ַ: http://quote.eastmoney.com/center/gridlist.html#newshares

����: �����Ƹ���-�¹�-ʵʱ��������

����: ���η��������¹����й�˾��ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_new_a_spot_em_df = ak.stock_new_a_spot_em()
print(stock_new_a_spot_em_df)
```

5���ӿ�: stock_cy_a_spot_em
�ӿ��������������Ƹ���-��ҵ��-ʵʱ����

Ŀ���ַ: https://quote.eastmoney.com/center/gridlist.html#gem_board

����: �����Ƹ���-��ҵ��-ʵʱ����

����: ���η������д�ҵ���ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_cy_a_spot_em_df = ak.stock_cy_a_spot_em()
print(stock_cy_a_spot_em_df)
```

6���ӿ�: stock_kc_a_spot_em
�ӿ��������������Ƹ���-�ƴ���-ʵʱ����

Ŀ���ַ: http://quote.eastmoney.com/center/gridlist.html#kcb_board

����: �����Ƹ���-�ƴ���-ʵʱ����

����: ���η������пƴ����ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_kc_a_spot_em_df = ak.stock_kc_a_spot_em()
print(stock_kc_a_spot_em_df)
```

7���ӿ�: stock_zh_ah_spot_em
�ӿ��������������Ƹ���-�����ͨ-AH�ɱȼ�-ʵʱ����

Ŀ���ַ: https://quote.eastmoney.com/center/gridlist.html#ah_comparison

����: �����Ƹ���-��������-�����ͨ-AH�ɱȼ�-ʵʱ����, �ӳ� 15 ���Ӹ���

����: ���η������� A+H ���й�˾��ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_zh_ah_spot_em_df = ak.stock_zh_ah_spot_em()
print(stock_zh_ah_spot_em_df)
```

8���ӿ�: stock_zh_ab_comparison_em
�ӿ��������������Ƹ���-�������-ȫ��AB�ɱȼ�

Ŀ���ַ: https://quote.eastmoney.com/center/gridlist.html#ab_comparison

����: �����Ƹ���-��������-�������-AB�ɱȼ�-ȫ��AB�ɱȼ�

����: ���η���ȫ�� AB �ɱȼ۵�ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_zh_ab_comparison_em_df = ak.stock_zh_ab_comparison_em()
print(stock_zh_ab_comparison_em_df)
```

9���ӿ�: stock_zh_a_new
�ӿ������������˲ƾ�-�������-���¹�-ʵʱ����

Ŀ���ַ: http://vip.stock.finance.sina.com.cn/mkt/#new_stock

����: ���˲ƾ�-��������-�������-���¹�

����: ���η������д��¹���������, ���ڴ��¹��������Ž����ձ仯���仯��ֻ�ܻ�ȡ��������յ�����

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_zh_a_new_df = ak.stock_zh_a_new()
print(stock_zh_a_new_df)

10���ӿ�: stock_zh_a_new_em
�ӿ��������������Ƹ���-�������-�¹�-ʵʱ����

Ŀ���ַ: https://quote.eastmoney.com/center/gridlist.html#newshares

����: �����Ƹ���-��������-�������-�¹�

����: ���η��ص�ǰ�������¹ɰ������й�Ʊ����������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_zh_a_new_em_df = ak.stock_zh_a_new_em()
print(stock_zh_a_new_em_df)
```

11���ӿ�: stock_xgsr_ths
�ӿ���������ͬ��˳-�¹�����-�¹���������

Ŀ���ַ: https://data.10jqka.com.cn/ipo/xgsr/

����: ͬ��˳-��������-�¹�����-�¹���������

����: ���η��ص�ǰ�����յ���������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_xgsr_ths_df = ak.stock_xgsr_ths()
print(stock_xgsr_ths_df)
```

### ����������

12���ӿ�: stock_zh_a_stop_em
�ӿ��������������Ƹ���-�������-����������
Ŀ���ַ: http://quote.eastmoney.com/center/gridlist.html#staq_net_board

����: �����Ƹ���-��������-�������-����������

����: ���η��ص�ǰ���������������е����й�Ʊ����������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |

�������

| ����     | ����      | ����      |
|--------|---------|---------|
| ���     | int64   | -       |
| ����     | object  | -       |
| ����     | object  | -       |
| ���¼�    | float64 | -       |
| �ǵ���    | float64 | ע�ⵥλ: % |
| �ǵ���    | float64 | -       |
| �ɽ���    | float64 | -       |
| �ɽ���    | float64 | -       |
| ���     | float64 | ע�ⵥλ: % |
| ���     | float64 | -       |
| ���     | float64 | -       |
| ��     | float64 | -       |
| ����     | float64 | -       |
| ����     | float64 | -       |
| ������    | float64 | ע�ⵥλ: % |
| ��ӯ��-��̬ | float64 | -       |
| �о���    | float64 | -       |

�ӿ�ʾ��

```python
import akshare as ak

stock_zh_a_stop_em_df = ak.stock_zh_a_stop_em()
print(stock_zh_a_stop_em_df)
```

����ʾ��

```
      ��� ����    ����      ���¼� �ǵ��� �ǵ���  ... �� ���� ���� ������ ��ӯ��-��̬�о���
0      1  400010  ��  �� 5  1.90  4.97  0.09  ... NaN  1.81 NaN  NaN  -87.16  20.41
1      2  400069     ����5  9.96  4.95  0.47  ... NaN  9.49 NaN  NaN   19.61   3.78
2      3  400073    ����A5  7.08  4.89  0.33  ... NaN  6.75 NaN  NaN   97.79  11.69
3      4  400008   ˮ�ɣ� 5  4.96  4.86  0.23  ... NaN  4.73 NaN  NaN -539.13  992.0
4      5  400059     ����5  3.50  4.79  0.16  ... NaN  3.34 NaN  NaN   50.29   3.72
..   ...     ...     ...   ...   ...   ...  ...  ..   ...  ..  ...     ...    ...
100  101  400027  ��  ̬ 5  1.05 -4.55 -0.05  ... NaN   1.1 NaN  NaN  -57.07    4.7
101  102  400036     �촴5  1.64 -4.65 -0.08  ... NaN  1.72 NaN  NaN   103.8   1.57
102  103  400005   ����ʵ 5  1.01 -4.72 -0.05  ... NaN  1.06 NaN  NaN  -91.82   15.3
103  104  400039  ��  ʥ 5  0.95 -5.00 -0.05  ... NaN   1.0 NaN  NaN  -65.97   4.64
104  105  400028  ��  �� 5  0.95 -5.00 -0.05  ... NaN   1.0 NaN  NaN -226.19    9.3
```

13���ӿ�: stock_hk_spot_em
�ӿ��������������Ƹ�-�۹�-ʵʱ����(��15���ӣ�

Ŀ���ַ: http://quote.eastmoney.com/center/gridlist.html#hk_stocks

����: ���и۹ɵ�ʵʱ��������; �������� 15 ������ʱ

����: ���η�����������յ����и۹ɵ�����

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_hk_spot_em_df = ak.stock_hk_spot_em()
print(stock_hk_spot_em_df)
```

14���ӿ�: stock_hk_main_board_spot_em
�ӿ��������������Ƹ�-�۹�����-ʵʱ����(��15���ӣ�

Ŀ���ַ: https://quote.eastmoney.com/center/gridlist.html#hk_mainboard

����: �۹������ʵʱ��������; �������� 15 ������ʱ

����: ���η��ظ۹����������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_hk_main_board_spot_em_df = ak.stock_hk_main_board_spot_em()
print(stock_hk_main_board_spot_em_df)
```

#### ֪���۹�

15���ӿ�: stock_hk_famous_spot_em
�ӿ��������������Ƹ���-֪���۹�ʵʱ��������
Ŀ���ַ: https://quote.eastmoney.com/center/gridlist.html#hk_wellknown

����: �����Ƹ���-��������-�۹��г�-֪���۹�ʵʱ��������

����: ���η���ȫ����������

�������

| ���� | ���� | ���� |
|----|----|----|
| -  | -  | -  |

�������

| ����  | ����      | ����       |
|-----|---------|----------|
| ���  | int64   | -        |
| ����  | object  | -        |
| ����  | object  | -        |
| ���¼� | float64 | ע�ⵥλ: ��Ԫ |
| �ǵ��� | float64 | ע�ⵥλ: ��Ԫ |
| �ǵ��� | float64 | ע�ⵥλ: %  |
| ��  | float64 | ע�ⵥλ: ��Ԫ |
| ���  | float64 | ע�ⵥλ: ��Ԫ |
| ���  | float64 | ע�ⵥλ: ��Ԫ |
| ����  | float64 | ע�ⵥλ: ��Ԫ |
| �ɽ��� | float64 | ע�ⵥλ: ��  |
| �ɽ��� | float64 | ע�ⵥλ: ��Ԫ |

�ӿ�ʾ��

```python
import akshare as ak

stock_hk_famous_spot_em_df = ak.stock_hk_famous_spot_em()
print(stock_hk_famous_spot_em_df)
```

����ʾ��

```
      ��� ����       ����    ���¼�  ...    ���     ����    �ɽ���           �ɽ���
0      1  01918      �ڴ��й�   2.04  ...   1.91   1.91  633638656.0  1.295074e+09
1      2  00763      ����ͨѶ  34.65  ...  31.50  32.85   90643056.0  3.088137e+09
2      3  00753      �й�����   4.56  ...   4.25   4.33   34639744.0  1.560062e+08
3      4  01928  ��ɳ�й����޹�˾  18.08  ...  17.20  17.18   37260253.0  6.721171e+08
4      5  03900      �̳��й�  10.38  ...   9.89   9.91   33031905.0  3.421672e+08
..   ...    ...       ...    ...  ...    ...    ...          ...           ...
113  114  02400      �Ķ���˾  32.15  ...  31.60  34.20    4769000.0  1.544492e+08
114  115  01833     ƽ����ҽ��   8.68  ...   8.55   9.31   53910271.0  4.845739e+08
115  116  02269      ҩ������  23.65  ...  23.10  26.00  170040773.0  4.052070e+09
116  117  02359      ҩ������  62.90  ...  62.40  70.00   20403989.0  1.314193e+09
117  118  09698   �������-SW  42.70  ...  41.30  48.30   24768786.0  1.068253e+09
[118 rows x 12 columns]
```
16���ӿ� stock_us_spot_em
�ӿ��������������Ƹ���-����-ʵʱ����

Ŀ���ַ: https://quote.eastmoney.com/center/gridlist.html#us_stocks

����: �����Ƹ���-����-ʵʱ����

����: ���η��������������й�˾��ʵʱ��������

�������

| ����  | ����  | ����  |
|-----|-----|-----|
| -   | -   | -   |
�ӿ�ʾ����
```python
import akshare as ak

stock_us_spot_em_df = ak.stock_us_spot_em()
print(stock_us_spot_em_df)
```

#### ֪������

17���ӿ�: stock_us_famous_spot_em
�ӿ��������������Ƹ���-֪�����ɵ�ʵʱ��������
Ŀ���ַ: http://quote.eastmoney.com/center/gridlist.html#us_wellknown

����: ����-֪�����ɵ�ʵʱ��������

����: ���η���ָ�� symbol ����������

�������

| ����     | ����  | ����                                                                       |
|--------|-----|--------------------------------------------------------------------------|
| symbol | str | symbol="�Ƽ���"; choice of {'�Ƽ���', '������', 'ҽҩʳƷ��', 'ý����', '������Դ��', '����������'} |

�������

| ����  | ����      | ����              |
|-----|---------|-----------------|
| ���  | int64   | -               |
| ����  | object  | -               |
| ���¼� | float64 | ע�ⵥλ: ��Ԫ        |
| �ǵ��� | float64 | ע�ⵥλ: ��Ԫ        |
| �ǵ��� | float64 | ע�ⵥλ: %         |
| ���̼� | float64 | ע�ⵥλ: ��Ԫ        |
| ��߼� | float64 | ע�ⵥλ: ��Ԫ        |
| ��ͼ� | float64 | ע�ⵥλ: ��Ԫ        |
| ���ռ� | float64 | ע�ⵥλ: ��Ԫ        |
| ����ֵ | float64 | ע�ⵥλ: ��Ԫ        |
| ��ӯ�� | float64 | -               |
| ����  | object  | ע��: ������ȡ��ʷ���ݵĴ��� |

�ӿ�ʾ��

```python
import akshare as ak

stock_us_famous_spot_em_df = ak.stock_us_famous_spot_em(symbol='�Ƽ���')
print(stock_us_famous_spot_em_df)
```

����ʾ��

```
    ���              ����           ���¼�  ...         ����ֵ     ��ӯ��        ����
0    1  Silvergate Capital Corp-A   116.34  ...     3085409047   61.93    106.SI
1    2  Opendoor Technologies Inc    18.94  ...    11451903533  -19.65  105.OPEN
2    3                     ���ո��Ἴ��    17.55  ...     2233160842   -1.82   106.ATI
3    4                Yandex NV-A    78.71  ...    28129406798  131.13  105.YNDX
4    5                        ������    11.83  ...    39443015025   16.44  105.ERIC
5    6                        ŵ����     5.91  ...    33269348763  -14.11   106.NOK
6    7              Groupon Inc-A    22.16  ...      654264338   73.65  105.GRPN
7    8                         ����    62.46  ...    49840992399  129.65  106.TWTR
8    9             Facebook Inc-A   378.00  ...  1065750021378   27.36    105.FB
9   10                         ����    28.21  ...    32512553599    7.98   106.HPQ
10  11                       �ȸ�-C  2898.27  ...  1932435735616   16.84  105.GOOG
11  12                      ����������   113.38  ...    18461647373   31.60  105.AKAM
12  13                      �����뵼��   106.15  ...   128756264684   37.47   105.AMD
13  14                         ˼��    58.60  ...   247159324736   23.34  105.CSCO
14  15                       �л�����    40.05  ...    31068573413   24.84   106.CHT
15  16                       ��������   188.47  ...   173997383234   25.87   105.TXN
16  17                        �¶��   661.68  ...   315224352000   56.47  105.ADBE
17  18                        ��֪��    76.48  ...    40197673856   23.91  105.CTSH
18  19                        Ӣ�ض�    53.40  ...   216643800000   11.68  105.INTC
19  20                     �����绰�籨    27.42  ...   195778800000 -100.55     106.T
20  21                         ��ͨ   141.58  ...   159702240000   17.35  105.QCOM
21  22                         ƻ��   154.07  ...  2546802675620   29.34  105.AAPL
22  23              IBM������ҵ����(US)   137.74  ...   123459126717   23.15   106.IBM
23  24                         ����    60.28  ...    44955123381   10.96   106.DOW
24  25                        ˼����   145.68  ...   171841118251   23.58   106.SAP
25  26                        Ӣΰ��   221.77  ...   554425000000   78.33  105.NVDA
26  27                      ����ɭͨѶ    54.44  ...   225387915421   11.28    106.VZ
27  28                         ΢��   297.25  ...  2233801423468   36.46  105.MSFT
28  29                   Ħ�������������   244.00  ...    41315202400   35.80   106.MSI
29  30                        ����ѷ  3484.16  ...  1764519802163   59.94  105.AMZN
30  31                         ��Ȥ    73.00  ...    47454073765    3.68  105.EBAY
31  32                    �ִ��(US)    16.61  ...    46152628937  351.55   105.VOD
32  33                Zynga Inc-A     8.28  ...     9040854574  -53.06  105.ZNGA
33  34          SentinelOne Inc-A    66.04  ...    16930759265  -85.17     106.S
```
