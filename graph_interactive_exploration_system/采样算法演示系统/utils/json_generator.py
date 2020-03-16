import re, json,os

# 将原始svg文件转化为json格式文件，以便服务于鱼眼特效
class JSON_Generator():
    def __init__(self):
        self.json_record = {
            "svg_width": "",
            "svg_height": "",
            "svg_viewBox": "",
            "nodes": [],
            "links": [],
        }

    def convertion(self, svg_file_path, json_output_path):
        # 获取svg头信息
        with open(svg_file_path, 'r', encoding='utf-8')as fp:
            svg_text = fp.readline()
            svg_header = ''
            while ('version="1.1"' not in svg_text):
                svg_header += svg_text
                svg_text = fp.readline()
            svg_header += svg_text
        self.json_record['svg_width'] = re.findall('width="(.*)"', svg_header)[0]
        self.json_record['svg_height'] = re.findall('height="(.*)"', svg_header)[0]
        self.json_record['svg_viewBox'] = re.findall('viewBox="([\-\.0-9 ]*)"', svg_header)[0]

        # 获取节点和边信息
        with open(svg_file_path, 'r', encoding='utf-8')as fp:
            svg_text = fp.read()
            edges = re.findall('<path .*\n.*\n.*/>', svg_text)
            nodes = re.findall('<circle .*\n.*\n.*/>', svg_text)

            # 重定向节点id（从0开始）
            node_num = {}
            index = 0
            for _ in nodes:
                node_id = re.findall('class="id_([0-9]*)"', _)[0]
                node_num[node_id] = index
                index += 1

            for _ in nodes:
                node_id = re.findall('class="(id_[0-9]*)"', _)[0]
                node_cx = re.findall('cx="(-{0,1}[0-9]*\.{0,1}[0-9]*)"', _)[0]
                node_cy = re.findall('cy="(-{0,1}[0-9]*\.{0,1}[0-9]*)"', _)[0]
                node_r = re.findall('r="([0-9]*\.{0,1}[0-9]*)"', _)[0]
                self.json_record["nodes"].append({
                    "id": node_id,
                    "cx": node_cx,
                    "cy": node_cy,
                    "r": node_r
                })
            print(self.json_record["nodes"])
            for _ in edges:
                edge_num = re.findall('class="id_([0-9]*) id_([0-9]*)"', _)[0]
                self.json_record['links'].append({
                    "source": node_num[edge_num[0]],
                    "target": node_num[edge_num[1]],
                    "weight": 1
                })
        # 将结果写入json文件
        node_record_json = json.dumps(self.json_record, ensure_ascii=False)
        with open(json_output_path, 'w', encoding='utf-8')as json_fp:
            json.dump(node_record_json, json_fp)
        # 替换json文件中的收尾双引号和反斜杠
        with open(json_output_path, 'r', encoding='utf-8')as json_fp:
            json_text = json_fp.read()
        with open(json_output_path, 'w', encoding='utf-8')as json_fp:
            json_fp.write(json_text[1:-1].replace("\\", ""))


# if __name__ == '__main__':
#     svg_filelist = os.listdir('../frontend/public/static/graph_set/svg/cspan/')
#     print(svg_filelist)
#     for file in svg_filelist:
#         generator = JSON_Generator()
#         source_svg_path = '../frontend/public/static/graph_set/svg/cspan/'+file
#         target_json_path = '../frontend/public/static/graph_set/json/cspan/'+file.replace(".svg",".json")
#         generator.convertion(source_svg_path, target_json_path)
