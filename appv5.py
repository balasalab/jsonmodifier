import json
import sys
import logging

logging.basicConfig(filename="jsonmapping.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

class JsonFormat(object):
	"""docstring for JsonFormat"""
	def __init__(self):
		super(JsonFormat, self).__init__()
	
	def check_data_type(self, data):
		if isinstance(data, dict):
			return "dict"
		elif isinstance(data, list):
			return "list"
		elif isinstance(data, str):
			return "string"
		elif isinstance(data, set):
			return "set"



class ReadJson(JsonFormat):
	def __init__(self, input_json):
		super(ReadJson, self).__init__()
		self.input_json = input_json
		self.autojson={}
		self.load()

	def load(self):
		self.recursive(self.input_json, None)

	def recursive(self, data, pathkey=None):
		if self.check_data_type(data) == "dict":
			for key, value in data.items():
				pk=pathkey+"|"+key if pathkey else key
				self.recursive(value, pk)
		elif self.check_data_type(data) == "list":
			i=0
			for key in data:
				if isinstance(key, dict):
					pk=pathkey+"|"+str(i) if pathkey else str(i)
				else:
					pk=pathkey+"|"+str(i) if pathkey else key
				self.recursive(key, pk)
				i+=1
		else:
			self.autojson[pathkey]=data


class ComposeJson(ReadJson):
	"""docstring for ComposeJson"""
	def __init__(self, input_json, output_template):
		super(ComposeJson, self).__init__(input_json)
		self.output_template = output_template

	def load_output_template(self):
		if self.check_data_type(self.output_template) == "dict":
			logger.debug("output_template dict type")
			res={}
			res=self.read_dict_data(self.output_template, res)
			return (json.dumps(res))

		elif self.check_data_type(self.output_template) == "list":
			logger.debug("output_template list type")
			res=[]
			keys=self.output_template[0].split("*")
			self.read_data(keys[0], keys, 1, res)
			return (res)
		elif self.check_data_type(self.output_template) == "set":
			res = self.read_set_data(self.output_template)
			return json.dumps(res)
		else:
			logger.debug("output_template type not comppatible", type(self.output_template))

	def read_data(self, composed_key, key, index, res):
		autojson_length=len(self.autojson)
		for i in range(autojson_length):
			ck = (composed_key+str(i)+key[index])
			if len(key)>index+1:
				self.read_data(ck, key, index+1, res)
			else:
				if ck in self.autojson:
					res.append(self.autojson[ck])

	def add_index_in_keys(self, key):
		temp=[]
		keys  = key.split("*", 1)
		autojson_length=len(self.autojson)
		if len(keys)>1:
			for i in range(autojson_length):
				comk = keys[0]+str(i)+keys[1]
				sck = comk.split("*", 1)
				if len(sck) > 1:
					temp = temp+self.add_index_in_keys(comk)
				else:
					new_key = keys[0]+str(i)+keys[1]
					if new_key in self.autojson or "*" in new_key:
						temp.append(new_key)
					# temp.append(new_key)
		else:
			temp=temp+[key]
		return temp

	def read_set_data(self, output_template):
		tmp_res={}
		for key in output_template:
			for composed_key in self.add_index_in_keys(key):
				if composed_key in self.input_json:
					tmp_res[composed_key] = (self.input_json[composed_key])
				else:
					s_composed_key = composed_key.split("|")[-1]
					tmp_res[s_composed_key] = (self.autojson[composed_key])
		return tmp_res

	def read_dict_data(self, output_template, res, previous_key=None):
		temp={}
		for fkey, fval in output_template.items():
			logger.debug(fkey)
			logger.debug(fval)

			#=======
			spkey = fkey.split("-")
			fkey = spkey[0]
			#=======

			for composed_key in self.add_index_in_keys(fkey):

				if composed_key in self.autojson:
					keydata = (self.autojson[composed_key])
				else:
					s_composed_key = composed_key.split("|")[-1]
					keydata = s_composed_key

				#=== parse
				if len(spkey)>1:
					p_keydata = self.key_data_parse(keydata, spkey[1])
					keydata = p_keydata
				#=== parse

				if isinstance(fval, dict):
					if keydata not in temp:
						temp[keydata]={}

					temp[keydata] = { **temp[keydata], **self.read_dict_data(fval, [], composed_key)}
				elif isinstance(fval, list):
					if keydata not in temp:
						temp[keydata]=[]
					temp[keydata] = temp[keydata]+self.read_list_data(fval, composed_key)
				elif isinstance(fval, str):
					if self.isSubSet(previous_key, composed_key):
						temp[keydata] = self.read_str_data(fval, composed_key)
				elif isinstance(fval, set):
					if self.isSubSet(previous_key, composed_key):
						temp[keydata] = self.read_set_data(fval)
				else:
					logger.debug("value type not matched "+str(type(fval)))
		# print(temp)
		return temp
			#========

	def read_list_data(self, key, composed_key):
		temp=[]
		if isinstance(key[0], dict):
			res = self.read_dict_data(key[0], [], composed_key)
			temp.append(res)
		else:
			keys = self.add_index_in_keys(key[0])
			for k in keys:
				if self.isSubSet(composed_key, k):
					# print(composed_key, k, self.autojson[k])
					temp.append(self.autojson[k])
		return temp

	def read_str_data(self, key, composed_key):
		temp=[]
		keys = self.add_index_in_keys(key)
		for k in keys:
			if self.isSubSet(composed_key, k):
				# print(composed_key, k, self.autojson[k])
				temp.append(self.autojson[k])
		return temp[0] if len(temp)==1 else temp


	def isSubSet(self, key1, key2):
		if not key1 or not key2:
			return True
		sk1 = key1.split("|")
		sk2 = key2.split("|")
		skl = len(sk1)
		for i in range(skl):
			if  sk1[i]!=sk2[i]:
				if (sk1[i].isnumeric()):
					return False
				else:
					return True
				break
			elif  sk1[i]==sk2[i]:
				if i+1 == skl:
					return True

	def key_data_parse(self, keydata, oper):
		s_oper = oper.split(" ")
		if s_oper[0]=="split":
			s_keydata = keydata.split(s_oper[1])
			return s_keydata[int(s_oper[2])]
