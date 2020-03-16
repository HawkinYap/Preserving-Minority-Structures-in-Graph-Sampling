import csv, os

if __name__ == '__main__':
    file_list = list(filter(lambda item: "_edge.csv" in item, os.listdir("./")))
    if "new_edges" not in os.listdir("./"):
        os.mkdir("new_edges")
    for file in file_list:
        with open("./" + file, 'r', encoding='utf-8')as fp_read:
            reader = csv.reader(fp_read)
            next(reader)
            edges_list = set()
            for row in reader:
                if (row[0], row[1]) not in edges_list and (row[1], row[0]) not in edges_list:
                    edges_list.add((row[0], row[1]))
            with open('./new_edges/{}'.format(file), 'w', encoding='utf-8', newline='')as fp_write:
                writer = csv.writer(fp_write)
                writer.writerow(['source', 'target'])
                writer.writerows(list(edges_list))
