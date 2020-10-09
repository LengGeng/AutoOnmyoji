class TargetException(Exception):
    pass


class Docs:
    """
    Does 获取类、函数的文档对象
    """
    __doc_all__ = ["parse", "parses"]

    def __init__(self, target=None):
        self.target = target

    @staticmethod
    def __parse(doc_text):
        """解析DOC文档
        将__doc___中的doc文档解析成对象
        :param doc_text: doc文档
        :type doc_text: str
        :return: doc对象
        """
        name = None
        desc = ""
        args = {}
        result = None
        for doc_line in doc_text.splitlines():
            if doc_line.startswith("    ") or doc_line.startswith("\t"):
                doc_line = doc_line.lstrip("\t").lstrip()
                # 参数说明
                if doc_line.startswith(":param"):
                    arg_name, *arg_desc = doc_line[6:].split(":")
                    arg_name = arg_name.lstrip()
                    arg_desc = ":".join(arg_desc).lstrip()
                    if arg_name not in args:
                        args[arg_name] = {}
                    args[arg_name]["desc"] = arg_desc
                # 参数类型
                elif doc_line.startswith(":type"):
                    arg_name, *arg_desc = doc_line[6:].split(":")
                    arg_name = arg_name.lstrip()
                    arg_type = ":".join(arg_desc).lstrip()
                    if arg_name not in args:
                        args[arg_name] = {}
                    args[arg_name.lstrip()]["type"] = arg_type
                # return
                elif doc_line.startswith(":return"):
                    doc_line = doc_line[7:].lstrip(":")
                    if doc_line:
                        result = doc_line
                # 详情描述
                else:
                    desc += "\n" + doc_line
            # 基本描述
            else:
                if doc_line.strip() == '':
                    doc_line = None
                if name is None:
                    name = doc_line
        # 过滤没有介绍的参数
        args = {k: v for k, v in args.items() if v.get("desc") is not None}
        return {"name": name, "desc": desc.strip(), "args": args, "return": result}

    def __get_doc(self, method):
        """
        返回方法的doc文档
        :param method: 方法名 若是字符串,需要先指定目标对象.function对象则不需要.
        :return: doc文档
        """
        method_type = str(type(method))
        if method_type == "<class 'function'>" or method_type == "<class 'type'>":
            return method.__doc__
        elif type(method) == str:
            if self.target is not None:
                if hasattr(self.target, method):
                    return getattr(self.target, method).__doc__
            else:
                raise TargetException("target is None")

    def parse(self, method):
        """
        解析方法的doc文档
        :param method: 方法名
        :type method: str or fun
        :return: 方法的文档对象
        """
        doc_text = self.__get_doc(method)
        return {"function": method, **self.__parse(doc_text)} if doc_text else None

    def parses(self, *methods):
        """
        同时解析多个方法
        :param methods: 多个方法
        :type methods: str or type
        :return: 多个方法文档的生成器
        """
        docs = []
        for method in methods:
            docs.append(self.parse(method))
        return docs

    def getall(self):
        """获取目标类的所有方法文档
        获取目标类的所有方法文档
        由类的__doc_all__属性指定,没有指定时获取类中所有不以_开头的函数
        :return:
        """
        if self.target is None:
            raise TargetException("target is None")
        __all__ = getattr(self.target, "__doc_all__") if hasattr(self.target, "__doc_all__") else [
            fun for fun in dir(self.target) if not fun.startswith("_")]
        return self.parses(*__all__)


def _test():
    from pprint import pprint

    does = Docs(Docs)
    # does_list = does.getall()
    does_list = does.parses("parse", "parses")
    pprint(does_list)


if __name__ == '__main__':
    _test()
