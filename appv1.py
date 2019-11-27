import json
import sys

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
			res={}
			res=self.read_dict_data(self.output_template, res)
			print(json.dumps(res))

		elif self.check_data_type(self.output_template) == "list":
			res=[]
			keys=self.output_template[0].split("*")
			self.read_data(keys[0], keys, 1, res)
			print(res)

	def read_data(self, composed_key, key, index, res):
		autojson_length=len(self.autojson)
		for i in range(autojson_length):
			ck = (composed_key+str(i)+key[index])
			if len(key)>index+1:
				self.read_data(ck, key, index+1, res)
			else:
				if ck in self.autojson:
					res.append(self.autojson[ck])

	def get_data(self, composed_key, key, index, res):
		autojson_length=len(self.autojson)
		for i in range(autojson_length):
			ck = (composed_key+str(i)+key[index])
			print("str ==============", ck, len(key), index+1)
			if len(key)>index+1:
				self.get_data(ck, key, index+1, res)
			else:
				if ck in self.autojson:
					print(ck)
					yield (self.autojson[ck], i)

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


	def read_dict_data(self, output_template, res, previous_key=None):
		for fkey, fval in output_template.items():
			temp={}
			for composed_key in self.add_index_in_keys(fkey):
				if isinstance(fval, dict):
					keydata = (self.autojson[composed_key])
					
					if keydata not in temp:
						temp[keydata]={}

					temp[keydata] = { **temp[keydata], **self.read_dict_data(fval, [], composed_key)}
				elif isinstance(fval, list):
					keydata = (self.autojson[composed_key])
					if keydata not in temp:
						temp[keydata]=[]
					temp[keydata] = temp[keydata]+self.read_list_data(fval, composed_key)
				elif isinstance(fval, str):
					keydata = (self.autojson[composed_key])
					if self.isSubSet(previous_key, composed_key):
						temp[keydata] = self.read_str_data(fval, composed_key)
			# print(temp)
		return temp
			#========

	def read_list_data(self, key, composed_key):
		temp=[]
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
			

	def read_dict_data1(self, output_template, res, exit=None):
		for fkey, fval in output_template.items():
			keys = fkey.split("*")
			#========
			if len(keys) > 1:
				print("multiple values")
				# self.add_index_in_keys(fkey, [])
			else:
				print("single value")

			print(self.add_index_in_keys(fkey, []))
			sys.exit()
			#========

			for (v1, i) in self.get_data(keys[0], keys, 1, res):
				if isinstance(fval, str):
					print("str ==============")
					vkeys = fval.split("*")
					for v2,j in self.get_data(vkeys[0], vkeys, 1, res):
						# print(i,j, v1, v2)
						if(i==j):
							res[v1]=v2
				elif isinstance(fval, dict):
					print("dict ==============")
					res[v1]={}
					# print(fval)
					self.read_dict_data(fval, res[v1], True)
				else:
					print("asasdasdasd===========")


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


inp={"data":{"songs":[{"album":"petta","composer":"ani","year":"2019","song_name":"kalyanam","movie":{"name":"petta"},"actor":{"name":"rajini"},"award":["NTCA","OSCAR","IFFA"]},{"album":"petta","composer":"ani","year":"2019","song_name":"petta","movie":{"name":"petta"},"actor":{"name":"rajini"},"award":["NTCA","OSCAR","IFFA"]},{"album":"thegidi","composer":"nivas","year":"2016","song_name":"vinmeen","movie":{"name":"thegidi"},"actor":{"name":"ashok"},"award":["NTCA","IFFA"]},{"album":"thegidi","composer":"nivas","year":"2016","song_name":"nethane","movie":{"name":"thegidi"},"actor":{"name":"ashok"},"award":["NTCA","IFFA"]},{"album":"Maattrraan","composer":"harria","year":"2012","song_name":"theye","movie":{"name":"Maattrraan"},"actor":{"name":"surya"},"award":["IFFA"]},{"album":"Maattrraan","composer":"harria","year":"2012","song_name":"nani koni","movie":{"name":"Maattrraan"},"actor":{"name":"surya"},"award":["IFFA"]}]}}

output_template = ["data|songs|*|movie|name"]
output_template1 = ["data|songs|*|song_name"]
output_template1 = ["data|songs|*|award|*"]
output_template1 = {
	"data|songs|*|movie|name":"data|songs|*|year"
}

output_template1 = {
	"data|songs|*|movie|name":{
		"data|songs|*|song_name":"data|songs|*|year"
	}
}

output_template1 = {
	"data|songs|*|award|*":{
		"data|songs|*|song_name":"data|songs|*|year"
	}
}

output_template1 = {
	"data|songs|*|movie|name":[
		"data|songs|*|song_name"
	]
}

print("==*==")
rj = ComposeJson(inp, output_template)
# print(rj.autojson)
rj.load_output_template()
print("==*==")

		