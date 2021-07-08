基于彩绘图像生成纯色图像

## 运行环境
    python 3.7  
## 库
    PIL
    opencv-python
## 主程序
    main.py
## 使用说明
- 参考main.py中的入口函数flatImg()。
- flagImg的输入参数包括彩绘图文件、线框图文件以及一个参数集合体params。params
的各类参数请参看main.py。
- 如果params["save_colored_regions"]设置为True，则会保存一个文件名为：
彩绘文件名_small_regs.png的图像。该图像中用红色标注了面积小于指定参数params["area_thresh"]
的区域
- 结果文件以：原彩绘文件名_颜色数量_flatted.png 命名。
  参考效果如下所示：
![输入输出示意图](https://github.com/zjustarstar/PureColorExtractor/blob/main/result/demo.jpg)

## 其它说明
- 查找小面积区域时，由于线条边界不够清晰，会有一定程度的误判。如下图就是将
params["save_colored_regions"]设置为True时保存下来的图像，其中红色区域表示面积
过小。这就可能在最终的结果图中，存在某些很小的区域。
![小区域示意图](https://github.com/zjustarstar/PureColorExtractor/blob/main/result/small_regions.png)
    