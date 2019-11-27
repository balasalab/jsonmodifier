import logging
import json


class Config(object):
    """
    Default Configuration values 
    """
    param_split_by = "|"
    function_split_by = "@"
    logger = ""

    def __init__(self):
        super(Config, self).__init__()
        logging.basicConfig(filename="json_manipulate.log",
                            format='%(asctime)s | %(message)s', filemode='a')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)


class Param(Config):
    """
    Param class - 
    - to get the real key or value
    - to find full path
    - to find is param from json or static value
    - to get value of the key 
    """

    def __init__(self, value):
        super(Param, self).__init__()
        self.logger.debug("Given param value is "+str(value))
        self.value = value

    def get_single_param(self):
        only_param = self.get_only_param()
        split_value = only_param.split(self.param_split_by)
        self.logger.debug(str(self.value) +
                          ", real param string  : "+str(split_value))
        return split_value[-1].strip()

    def get_only_param(self):
        split_value = self.value.split(self.function_split_by)
        self.logger.debug(str(self.value) + ", functions : "+str(split_value))
        return split_value[0].strip()

    def functions(self):
        split_value = self.value.split(self.function_split_by)
        self.logger.debug(str(self.value) + ", functions : "+str(split_value))
        return split_value[1:]

    def full_path(self):
        self.logger.debug(str(self.value) + ", full path : ")
        pass

    def get_value_string(self):
        pass


class ReadJsonData(Config):
    """
    ReadJsonData
    - to convert input json data into single dict, 
    which contain key value pair 
    """

    def __init__(self, param_input_json):
        super(ReadJsonData, self).__init__()
        self.logger.debug("ComposeJson ==>")
        self.input_json = param_input_json
        self.single_dict_json = {}
        self.convert_json_to_single_dict(self.input_json)

    def convert_json_to_single_dict(self, param_data, param_path_key=None):
        # self.logger.debug("Given input json type : "+str(type(param_data)) + " param_path_key : " + str(param_path_key) )
        if isinstance(param_data, dict):
            for dict_key, dict_value in param_data.items():
                c_path_key = param_path_key+"|" + \
                    dict_key if param_path_key else dict_key
                self.convert_json_to_single_dict(dict_value, c_path_key)
        elif isinstance(param_data, list):
            list_index = 0
            for list_value in param_data:
                if isinstance(list_value, dict):
                    c_path_key = param_path_key+"|" + \
                        str(list_index) if param_path_key else str(list_index)
                else:
                    c_path_key = param_path_key+"|" + \
                        str(list_index) if param_path_key else list_value
                self.convert_json_to_single_dict(list_value, c_path_key)
                list_index += 1
        else:
            self.single_dict_json[param_path_key] = param_data


class ComposeJson(ReadJsonData):
	"""docstring for ComposeJson"""
	def __init__(self, param_input_json, param_out_template):
		super(ComposeJson, self).__init__(param_input_json)
		self.logger.debug("ComposeJson ==>")
		self.input_json = param_input_json
		self.out_template = param_out_template

		self.read_out_template(self.out_template)

	def add_index_in_keys(self, key):
		self.logger.debug("add index in key : "+str(key))
		temp=[]
		keys  = key.split("*", 1)
		autojson_length=len(self.single_dict_json)
		if len(keys)>1:
			for i in range(autojson_length):
				comk = keys[0]+str(i)+keys[1]
				sck = comk.split("*", 1)
				if len(sck) > 1:
					temp = temp+self.add_index_in_keys(comk)
				else:
					new_key = keys[0]+str(i)+keys[1]
					if new_key in self.single_dict_json or "*" in new_key:
						temp.append(new_key)
					# temp.append(new_key)
		else:
			temp=temp+[key]
		return temp

	def read_out_template(self, param_out_template, response=None):
		self.logger.debug("Reading output template...")
		self.logger.debug("output template type : "+str(type(param_out_template)))

		
		if isinstance(param_out_template, dict):
			response = {} if not response else response
			response=self.read_dict_data(param_out_template)
		elif isinstance(param_out_template, list):
			# res=self.read_dict_data(param_out_template, res)
			pass
		elif isinstance(param_out_template, set):
			# self.read_set_data()
			pass
		elif isinstance(param_out_template, str):
			# self.read_str_data()
			pass
		else:
			self.logger.debug("output template type not compatible")

		pass

	def read_dict_data(self, output_template, previous_key=None):
		response={}
		for dict_key, dict_value in output_template.items():

			p = Param(dict_key)
			key_param = p.get_only_param()
			print(key_param, "=========")

			for composed_key in self.add_index_in_keys(key_param):

				if composed_key not in self.single_dict_json:
					keydata = (self.single_dict_json[composed_key])
				else:
					s_composed_key = composed_key.split("|")[-1]
					keydata = p.get_single_param()

				print(keydata)
			pass
		pass

	def read_list_data(self):
		pass

	def read_set_data(self):
		pass

	def read_str_data(self):
		pass

# class ReadDict(object):
# 	"""docstring for ReadTemplate"""
# 	def __init__(self, param_template):
# 		super(ReadTemplate, self).__init__()
# 		self.template = param_template
# 		self.response={}
# 		self.load()

# 	def load(self):
# 		for dict_key, dict_value in self.template.items():


		