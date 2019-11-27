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
			print("output_template dict type")
			res={}
			res=self.read_dict_data(self.output_template, res)
			return (json.dumps(res))

		elif self.check_data_type(self.output_template) == "list":
			print("output_template list type")
			res=[]
			keys=self.output_template[0].split("*")
			self.read_data(keys[0], keys, 1, res)
			return (res)
		elif self.check_data_type(self.output_template) == "set":
			res = self.read_set_data(self.output_template)
			return json.dumps(res)
		else:
			print("output_template type not comppatible", type(self.output_template))

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
				tmp_res[composed_key] = (self.input_json[composed_key])
		return tmp_res

	def read_dict_data(self, output_template, res, previous_key=None):
		for fkey, fval in output_template.items():

			#=======
			spkey = fkey.split("-")
			fkey = spkey[0]
			#=======

			temp={}
			for composed_key in self.add_index_in_keys(fkey):

				keydata = (self.autojson[composed_key])

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


inp={"data":{"songs":[{"album":"petta","composer":"ani","year":"2019","song_name":"kalyanam","movie":{"name":"petta"},"actor":{"name":"rajini"},"award":["NTCA","OSCAR","IFFA"]},{"album":"petta","composer":"ani","year":"2019","song_name":"petta","movie":{"name":"petta"},"actor":{"name":"rajini"},"award":["NTCA","OSCAR","IFFA"]},{"album":"thegidi","composer":"nivas","year":"2016","song_name":"vinmeen","movie":{"name":"thegidi"},"actor":{"name":"ashok"},"award":["NTCA","IFFA"]},{"album":"thegidi","composer":"nivas","year":"2016","song_name":"nethane","movie":{"name":"thegidi"},"actor":{"name":"ashok"},"award":["NTCA","IFFA"]},{"album":"Maattrraan","composer":"harria","year":"2012","song_name":"theye","movie":{"name":"Maattrraan"},"actor":{"name":"surya"},"award":["IFFA"]},{"album":"Maattrraan","composer":"harria","year":"2012","song_name":"nani koni","movie":{"name":"Maattrraan"},"actor":{"name":"surya"},"award":["IFFA"]}]}}
# inp={"type":"tank","data":[{"id":"Tank.loc1.level","v":171,"t":1568099608056},{"id":"Tank.loc1.inlet","v":18,"t":1568099608056},{"id":"Tank.loc1.outlet","v":17,"t":1568099608056},{"id":"Tank.loc1.temperature","v":36.645,"t":1568099608056},{"id":"Tank.loc1.pressure","v":1676.93715,"t":1568099608056},{"id":"Tank.loc2.temperature","v":36.645,"t":1568099608056},{"id":"Tank.loc2.pressure","v":1676.93715,"t":1568099608056}]}
# inp={"employees":[{"name":"Shyam","email":"shyamjaiswal@gmail.com"},{"name":"Bob","email":"bob32@gmail.com"},{"name":"Jai","email":"jai87@gmail.com"}]}
# inp=[{"postId":1,"id":1,"name":"id labore ex et quam laborum","email":"Eliseo@gardner.biz","body":"laudantium enim quasi est quidem magnam voluptate ipsam eos\ntempora quo necessitatibus\ndolor quam autem quasi\nreiciendis et nam sapiente accusantium"},{"postId":1,"id":2,"name":"quo vero reiciendis velit similique earum","email":"Jayne_Kuhic@sydney.com","body":"est natus enim nihil est dolore omnis voluptatem numquam\net omnis occaecati quod ullam at\nvoluptatem error expedita pariatur\nnihil sint nostrum voluptatem reiciendis et"},{"postId":1,"id":3,"name":"odio adipisci rerum aut animi","email":"Nikita@garfield.biz","body":"quia molestiae reprehenderit quasi aspernatur\naut expedita occaecati aliquam eveniet laudantium\nomnis quibusdam delectus saepe quia accusamus maiores nam est\ncum et ducimus et vero voluptates excepturi deleniti ratione"},{"postId":1,"id":4,"name":"alias odio sit","email":"Lew@alysha.tv","body":"non et atque\noccaecati deserunt quas accusantium unde odit nobis qui voluptatem\nquia voluptas consequuntur itaque dolor\net qui rerum deleniti ut occaecati"},{"postId":1,"id":5,"name":"vero eaque aliquid doloribus et culpa","email":"Hayden@althea.biz","body":"harum non quasi et ratione\ntempore iure ex voluptates in ratione\nharum architecto fugit inventore cupiditate\nvoluptates magni quo et"},{"postId":1,"id":6,"name":"vero eaque aliquid doloribus et culpa","email":"Hayden@althea.biz","body":"architecto fugit inventore cupiditate\nvoluptates magni quo et"}]
# inp=[{"userId":1,"id":1,"title":"delectus aut autem","completed":"false"},{"userId":1,"id":2,"title":"quis ut nam facilis et officia qui","completed":"false"},{"userId":1,"id":3,"title":"fugiat veniam minus","completed":"false"},{"userId":1,"id":4,"title":"et porro tempora","completed":"true"},{"userId":1,"id":5,"title":"laboriosam mollitia et enim quasi adipisci quia provident illum","completed":"false"},{"userId":1,"id":6,"title":"qui ullam ratione quibusdam voluptatem quia omnis","completed":"false"},{"userId":1,"id":7,"title":"illo expedita consequatur quia in","completed":"false"},{"userId":1,"id":8,"title":"quo adipisci enim quam ut ab","completed":"true"},{"userId":1,"id":9,"title":"molestiae perspiciatis ipsa","completed":"false"},{"userId":1,"id":10,"title":"illo est ratione doloremque quia maiores aut","completed":"true"},{"userId":1,"id":11,"title":"vero rerum temporibus dolor","completed":"true"},{"userId":1,"id":12,"title":"ipsa repellendus fugit nisi","completed":"true"},{"userId":1,"id":13,"title":"et doloremque nulla","completed":"false"},{"userId":1,"id":14,"title":"repellendus sunt dolores architecto voluptatum","completed":"true"},{"userId":1,"id":15,"title":"ab voluptatum amet voluptas","completed":"true"},{"userId":1,"id":16,"title":"accusamus eos facilis sint et aut voluptatem","completed":"true"},{"userId":1,"id":17,"title":"quo laboriosam deleniti aut qui","completed":"true"},{"userId":1,"id":18,"title":"dolorum est consequatur ea mollitia in culpa","completed":"false"},{"userId":1,"id":19,"title":"molestiae ipsa aut voluptatibus pariatur dolor nihil","completed":"true"},{"userId":1,"id":20,"title":"ullam nobis libero sapiente ad optio sint","completed":"true"},{"userId":2,"id":21,"title":"suscipit repellat esse quibusdam voluptatem incidunt","completed":"false"},{"userId":2,"id":22,"title":"distinctio vitae autem nihil ut molestias quo","completed":"true"},{"userId":2,"id":23,"title":"et itaque necessitatibus maxime molestiae qui quas velit","completed":"false"},{"userId":2,"id":24,"title":"adipisci non ad dicta qui amet quaerat doloribus ea","completed":"false"},{"userId":2,"id":25,"title":"voluptas quo tenetur perspiciatis explicabo natus","completed":"true"},{"userId":2,"id":26,"title":"aliquam aut quasi","completed":"true"},{"userId":2,"id":27,"title":"veritatis pariatur delectus","completed":"true"},{"userId":2,"id":28,"title":"nesciunt totam sit blanditiis sit","completed":"false"},{"userId":2,"id":29,"title":"laborum aut in quam","completed":"false"},{"userId":2,"id":30,"title":"nemo perspiciatis repellat ut dolor libero commodi blanditiis omnis","completed":"true"},{"userId":2,"id":31,"title":"repudiandae totam in est sint facere fuga","completed":"false"},{"userId":2,"id":32,"title":"earum doloribus ea doloremque quis","completed":"false"},{"userId":2,"id":33,"title":"sint sit aut vero","completed":"false"},{"userId":2,"id":34,"title":"porro aut necessitatibus eaque distinctio","completed":"false"},{"userId":2,"id":35,"title":"repellendus veritatis molestias dicta incidunt","completed":"true"},{"userId":2,"id":36,"title":"excepturi deleniti adipisci voluptatem et neque optio illum ad","completed":"true"},{"userId":2,"id":37,"title":"sunt cum tempora","completed":"false"},{"userId":2,"id":38,"title":"totam quia non","completed":"false"},{"userId":2,"id":39,"title":"doloremque quibusdam asperiores libero corrupti illum qui omnis","completed":"false"},{"userId":2,"id":40,"title":"totam atque quo nesciunt","completed":"true"},{"userId":3,"id":41,"title":"aliquid amet impedit consequatur aspernatur placeat eaque fugiat suscipit","completed":"false"},{"userId":3,"id":42,"title":"rerum perferendis error quia ut eveniet","completed":"false"},{"userId":3,"id":43,"title":"tempore ut sint quis recusandae","completed":"true"},{"userId":3,"id":44,"title":"cum debitis quis accusamus doloremque ipsa natus sapiente omnis","completed":"true"},{"userId":3,"id":45,"title":"velit soluta adipisci molestias reiciendis harum","completed":"false"},{"userId":3,"id":46,"title":"vel voluptatem repellat nihil placeat corporis","completed":"false"},{"userId":3,"id":47,"title":"nam qui rerum fugiat accusamus","completed":"false"},{"userId":3,"id":48,"title":"sit reprehenderit omnis quia","completed":"false"},{"userId":3,"id":49,"title":"ut necessitatibus aut maiores debitis officia blanditiis velit et","completed":"false"},{"userId":3,"id":50,"title":"cupiditate necessitatibus ullam aut quis dolor voluptate","completed":"true"},{"userId":3,"id":51,"title":"distinctio exercitationem ab doloribus","completed":"false"},{"userId":3,"id":52,"title":"nesciunt dolorum quis recusandae ad pariatur ratione","completed":"false"},{"userId":3,"id":53,"title":"qui labore est occaecati recusandae aliquid quam","completed":"false"},{"userId":3,"id":54,"title":"quis et est ut voluptate quam dolor","completed":"true"},{"userId":3,"id":55,"title":"voluptatum omnis minima qui occaecati provident nulla voluptatem ratione","completed":"true"},{"userId":3,"id":56,"title":"deleniti ea temporibus enim","completed":"true"},{"userId":3,"id":57,"title":"pariatur et magnam ea doloribus similique voluptatem rerum quia","completed":"false"},{"userId":3,"id":58,"title":"est dicta totam qui explicabo doloribus qui dignissimos","completed":"false"},{"userId":3,"id":59,"title":"perspiciatis velit id laborum placeat iusto et aliquam odio","completed":"false"},{"userId":3,"id":60,"title":"et sequi qui architecto ut adipisci","completed":"true"},{"userId":4,"id":61,"title":"odit optio omnis qui sunt","completed":"true"},{"userId":4,"id":62,"title":"et placeat et tempore aspernatur sint numquam","completed":"false"},{"userId":4,"id":63,"title":"doloremque aut dolores quidem fuga qui nulla","completed":"true"},{"userId":4,"id":64,"title":"voluptas consequatur qui ut quia magnam nemo esse","completed":"false"},{"userId":4,"id":65,"title":"fugiat pariatur ratione ut asperiores necessitatibus magni","completed":"false"},{"userId":4,"id":66,"title":"rerum eum molestias autem voluptatum sit optio","completed":"false"},{"userId":4,"id":67,"title":"quia voluptatibus voluptatem quos similique maiores repellat","completed":"false"},{"userId":4,"id":68,"title":"aut id perspiciatis voluptatem iusto","completed":"false"},{"userId":4,"id":69,"title":"doloribus sint dolorum ab adipisci itaque dignissimos aliquam suscipit","completed":"false"},{"userId":4,"id":70,"title":"ut sequi accusantium et mollitia delectus sunt","completed":"false"},{"userId":4,"id":71,"title":"aut velit saepe ullam","completed":"false"},{"userId":4,"id":72,"title":"praesentium facilis facere quis harum voluptatibus voluptatem eum","completed":"false"},{"userId":4,"id":73,"title":"sint amet quia totam corporis qui exercitationem commodi","completed":"true"},{"userId":4,"id":74,"title":"expedita tempore nobis eveniet laborum maiores","completed":"false"},{"userId":4,"id":75,"title":"occaecati adipisci est possimus totam","completed":"false"},{"userId":4,"id":76,"title":"sequi dolorem sed","completed":"true"},{"userId":4,"id":77,"title":"maiores aut nesciunt delectus exercitationem vel assumenda eligendi at","completed":"false"},{"userId":4,"id":78,"title":"reiciendis est magnam amet nemo iste recusandae impedit quaerat","completed":"false"},{"userId":4,"id":79,"title":"eum ipsa maxime ut","completed":"true"},{"userId":4,"id":80,"title":"tempore molestias dolores rerum sequi voluptates ipsum consequatur","completed":"true"},{"userId":5,"id":81,"title":"suscipit qui totam","completed":"true"},{"userId":5,"id":82,"title":"voluptates eum voluptas et dicta","completed":"false"},{"userId":5,"id":83,"title":"quidem at rerum quis ex aut sit quam","completed":"true"},{"userId":5,"id":84,"title":"sunt veritatis ut voluptate","completed":"false"},{"userId":5,"id":85,"title":"et quia ad iste a","completed":"true"},{"userId":5,"id":86,"title":"incidunt ut saepe autem","completed":"true"},{"userId":5,"id":87,"title":"laudantium quae eligendi consequatur quia et vero autem","completed":"true"},{"userId":5,"id":88,"title":"vitae aut excepturi laboriosam sint aliquam et et accusantium","completed":"false"},{"userId":5,"id":89,"title":"sequi ut omnis et","completed":"true"},{"userId":5,"id":90,"title":"molestiae nisi accusantium tenetur dolorem et","completed":"true"},{"userId":5,"id":91,"title":"nulla quis consequatur saepe qui id expedita","completed":"true"},{"userId":5,"id":92,"title":"in omnis laboriosam","completed":"true"},{"userId":5,"id":93,"title":"odio iure consequatur molestiae quibusdam necessitatibus quia sint","completed":"true"},{"userId":5,"id":94,"title":"facilis modi saepe mollitia","completed":"false"},{"userId":5,"id":95,"title":"vel nihil et molestiae iusto assumenda nemo quo ut","completed":"true"},{"userId":5,"id":96,"title":"nobis suscipit ducimus enim asperiores voluptas","completed":"false"},{"userId":5,"id":97,"title":"dolorum laboriosam eos qui iure aliquam","completed":"false"},{"userId":5,"id":98,"title":"debitis accusantium ut quo facilis nihil quis sapiente necessitatibus","completed":"true"},{"userId":5,"id":99,"title":"neque voluptates ratione","completed":"false"},{"userId":5,"id":100,"title":"excepturi a et neque qui expedita vel voluptate","completed":"false"},{"userId":6,"id":101,"title":"explicabo enim cumque porro aperiam occaecati minima","completed":"false"},{"userId":6,"id":102,"title":"sed ab consequatur","completed":"false"},{"userId":6,"id":103,"title":"non sunt delectus illo nulla tenetur enim omnis","completed":"false"},{"userId":6,"id":104,"title":"excepturi non laudantium quo","completed":"false"},{"userId":6,"id":105,"title":"totam quia dolorem et illum repellat voluptas optio","completed":"true"},{"userId":6,"id":106,"title":"ad illo quis voluptatem temporibus","completed":"true"},{"userId":6,"id":107,"title":"praesentium facilis omnis laudantium fugit ad iusto nihil nesciunt","completed":"false"},{"userId":6,"id":108,"title":"a eos eaque nihil et exercitationem incidunt delectus","completed":"true"},{"userId":6,"id":109,"title":"autem temporibus harum quisquam in culpa","completed":"true"},{"userId":6,"id":110,"title":"aut aut ea corporis","completed":"true"},{"userId":6,"id":111,"title":"magni accusantium labore et id quis provident","completed":"false"},{"userId":6,"id":112,"title":"consectetur impedit quisquam qui deserunt non rerum consequuntur eius","completed":"false"},{"userId":6,"id":113,"title":"quia atque aliquam sunt impedit voluptatum rerum assumenda nisi","completed":"false"},{"userId":6,"id":114,"title":"cupiditate quos possimus corporis quisquam exercitationem beatae","completed":"false"},{"userId":6,"id":115,"title":"sed et ea eum","completed":"false"},{"userId":6,"id":116,"title":"ipsa dolores vel facilis ut","completed":"true"},{"userId":6,"id":117,"title":"sequi quae est et qui qui eveniet asperiores","completed":"false"},{"userId":6,"id":118,"title":"quia modi consequatur vero fugiat","completed":"false"},{"userId":6,"id":119,"title":"corporis ducimus ea perspiciatis iste","completed":"false"},{"userId":6,"id":120,"title":"dolorem laboriosam vel voluptas et aliquam quasi","completed":"false"},{"userId":7,"id":121,"title":"inventore aut nihil minima laudantium hic qui omnis","completed":"true"},{"userId":7,"id":122,"title":"provident aut nobis culpa","completed":"true"},{"userId":7,"id":123,"title":"esse et quis iste est earum aut impedit","completed":"false"},{"userId":7,"id":124,"title":"qui consectetur id","completed":"false"},{"userId":7,"id":125,"title":"aut quasi autem iste tempore illum possimus","completed":"false"},{"userId":7,"id":126,"title":"ut asperiores perspiciatis veniam ipsum rerum saepe","completed":"true"},{"userId":7,"id":127,"title":"voluptatem libero consectetur rerum ut","completed":"true"},{"userId":7,"id":128,"title":"eius omnis est qui voluptatem autem","completed":"false"},{"userId":7,"id":129,"title":"rerum culpa quis harum","completed":"false"},{"userId":7,"id":130,"title":"nulla aliquid eveniet harum laborum libero alias ut unde","completed":"true"},{"userId":7,"id":131,"title":"qui ea incidunt quis","completed":"false"},{"userId":7,"id":132,"title":"qui molestiae voluptatibus velit iure harum quisquam","completed":"true"},{"userId":7,"id":133,"title":"et labore eos enim rerum consequatur sunt","completed":"true"},{"userId":7,"id":134,"title":"molestiae doloribus et laborum quod ea","completed":"false"},{"userId":7,"id":135,"title":"facere ipsa nam eum voluptates reiciendis vero qui","completed":"false"},{"userId":7,"id":136,"title":"asperiores illo tempora fuga sed ut quasi adipisci","completed":"false"},{"userId":7,"id":137,"title":"qui sit non","completed":"false"},{"userId":7,"id":138,"title":"placeat minima consequatur rem qui ut","completed":"true"},{"userId":7,"id":139,"title":"consequatur doloribus id possimus voluptas a voluptatem","completed":"false"},{"userId":7,"id":140,"title":"aut consectetur in blanditiis deserunt quia sed laboriosam","completed":"true"},{"userId":8,"id":141,"title":"explicabo consectetur debitis voluptates quas quae culpa rerum non","completed":"true"},{"userId":8,"id":142,"title":"maiores accusantium architecto necessitatibus reiciendis ea aut","completed":"true"},{"userId":8,"id":143,"title":"eum non recusandae cupiditate animi","completed":"false"},{"userId":8,"id":144,"title":"ut eum exercitationem sint","completed":"false"},{"userId":8,"id":145,"title":"beatae qui ullam incidunt voluptatem non nisi aliquam","completed":"false"},{"userId":8,"id":146,"title":"molestiae suscipit ratione nihil odio libero impedit vero totam","completed":"true"},{"userId":8,"id":147,"title":"eum itaque quod reprehenderit et facilis dolor autem ut","completed":"true"},{"userId":8,"id":148,"title":"esse quas et quo quasi exercitationem","completed":"false"},{"userId":8,"id":149,"title":"animi voluptas quod perferendis est","completed":"false"},{"userId":8,"id":150,"title":"eos amet tempore laudantium fugit a","completed":"false"},{"userId":8,"id":151,"title":"accusamus adipisci dicta qui quo ea explicabo sed vero","completed":"true"},{"userId":8,"id":152,"title":"odit eligendi recusandae doloremque cumque non","completed":"false"},{"userId":8,"id":153,"title":"ea aperiam consequatur qui repellat eos","completed":"false"},{"userId":8,"id":154,"title":"rerum non ex sapiente","completed":"true"},{"userId":8,"id":155,"title":"voluptatem nobis consequatur et assumenda magnam","completed":"true"},{"userId":8,"id":156,"title":"nam quia quia nulla repellat assumenda quibusdam sit nobis","completed":"true"},{"userId":8,"id":157,"title":"dolorem veniam quisquam deserunt repellendus","completed":"true"},{"userId":8,"id":158,"title":"debitis vitae delectus et harum accusamus aut deleniti a","completed":"true"},{"userId":8,"id":159,"title":"debitis adipisci quibusdam aliquam sed dolore ea praesentium nobis","completed":"true"},{"userId":8,"id":160,"title":"et praesentium aliquam est","completed":"false"},{"userId":9,"id":161,"title":"ex hic consequuntur earum omnis alias ut occaecati culpa","completed":"true"},{"userId":9,"id":162,"title":"omnis laboriosam molestias animi sunt dolore","completed":"true"},{"userId":9,"id":163,"title":"natus corrupti maxime laudantium et voluptatem laboriosam odit","completed":"false"},{"userId":9,"id":164,"title":"reprehenderit quos aut aut consequatur est sed","completed":"false"},{"userId":9,"id":165,"title":"fugiat perferendis sed aut quidem","completed":"false"},{"userId":9,"id":166,"title":"quos quo possimus suscipit minima ut","completed":"false"},{"userId":9,"id":167,"title":"et quis minus quo a asperiores molestiae","completed":"false"},{"userId":9,"id":168,"title":"recusandae quia qui sunt libero","completed":"false"},{"userId":9,"id":169,"title":"ea odio perferendis officiis","completed":"true"},{"userId":9,"id":170,"title":"quisquam aliquam quia doloribus aut","completed":"false"},{"userId":9,"id":171,"title":"fugiat aut voluptatibus corrupti deleniti velit iste odio","completed":"true"},{"userId":9,"id":172,"title":"et provident amet rerum consectetur et voluptatum","completed":"false"},{"userId":9,"id":173,"title":"harum ad aperiam quis","completed":"false"},{"userId":9,"id":174,"title":"similique aut quo","completed":"false"},{"userId":9,"id":175,"title":"laudantium eius officia perferendis provident perspiciatis asperiores","completed":"true"},{"userId":9,"id":176,"title":"magni soluta corrupti ut maiores rem quidem","completed":"false"},{"userId":9,"id":177,"title":"et placeat temporibus voluptas est tempora quos quibusdam","completed":"false"},{"userId":9,"id":178,"title":"nesciunt itaque commodi tempore","completed":"true"},{"userId":9,"id":179,"title":"omnis consequuntur cupiditate impedit itaque ipsam quo","completed":"true"},{"userId":9,"id":180,"title":"debitis nisi et dolorem repellat et","completed":"true"},{"userId":10,"id":181,"title":"ut cupiditate sequi aliquam fuga maiores","completed":"false"},{"userId":10,"id":182,"title":"inventore saepe cumque et aut illum enim","completed":"true"},{"userId":10,"id":183,"title":"omnis nulla eum aliquam distinctio","completed":"true"},{"userId":10,"id":184,"title":"molestias modi perferendis perspiciatis","completed":"false"},{"userId":10,"id":185,"title":"voluptates dignissimos sed doloribus animi quaerat aut","completed":"false"},{"userId":10,"id":186,"title":"explicabo odio est et","completed":"false"},{"userId":10,"id":187,"title":"consequuntur animi possimus","completed":"false"},{"userId":10,"id":188,"title":"vel non beatae est","completed":"true"},{"userId":10,"id":189,"title":"culpa eius et voluptatem et","completed":"true"},{"userId":10,"id":190,"title":"accusamus sint iusto et voluptatem exercitationem","completed":"true"},{"userId":10,"id":191,"title":"temporibus atque distinctio omnis eius impedit tempore molestias pariatur","completed":"true"},{"userId":10,"id":192,"title":"ut quas possimus exercitationem sint voluptates","completed":"false"},{"userId":10,"id":193,"title":"rerum debitis voluptatem qui eveniet tempora distinctio a","completed":"true"},{"userId":10,"id":194,"title":"sed ut vero sit molestiae","completed":"false"},{"userId":10,"id":195,"title":"rerum ex veniam mollitia voluptatibus pariatur","completed":"true"},{"userId":10,"id":196,"title":"consequuntur aut ut fugit similique","completed":"true"},{"userId":10,"id":197,"title":"dignissimos quo nobis earum saepe","completed":"true"},{"userId":10,"id":198,"title":"quis eius est sint explicabo","completed":"true"},{"userId":10,"id":199,"title":"numquam repellendus a magnam","completed":"true"},{"userId":10,"id":200,"title":"ipsam aperiam voluptates qui","completed":"false"}]


output_template1 = ["data|songs|*|movie|name"]
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

output_template = {
	"data|songs|*|movie|name":[
		"data|songs|*|song_name"
	]
}

output_template1 = {
	"data|songs|*|movie|name":[
		{
			"data|songs|*|song_name":"data|songs|*|year"
		}
	]
}

output_template1 = {
    "data|*|id-split . 1":{
        "data|*|id-split . 2":"data|*|v"
    }
}

output_template1 = {
	"employees|*|name":"employees|*|email"
}

output_template1 = {
	"*|name":["*|body"]
}
output_template1 = {
	"*|completed":{"*|title"}
}



# inp={"schemas":["urn:ietf:params:scim:schemas:extension:gluu:2.0:User","urn:ietf:params:scim:schemas:core:2.0:User"],"userName":"something@mailinator.com","name":{"givenName":"somthg","familyName":"sometghing"},"displayName":"smt sell","active":"true","password":"versa@123","phoneNumbers":[{"value":"9966335544"}],"emails":[{"value":"something@mailinator.com"}],"roles":[{"value":"Reseller","primary":"true"}],"urn:ietf:params:scim:schemas:extension:gluu:2.0:User":{"uniqueUserId":"36","mobile":"9966335544","street":"1","roomNumber":"Versa Store","company":"somtng","customerId":"somtng","countryCode":"91"}}
# output_template={
# 	"schemas",
# 	"userName"
# }

print("==*==")
rj = ComposeJson(inp, output_template)
# print(rj.autojson)
fo = rj.load_output_template()
print(fo)
print("==*==")

		