#!/usr/bin/env python
import json, os, math
from collections import OrderedDict
import numpy as np
from BackEndData import NAMESPACE, G
from Body import Body

try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    unicode = str
    basestring = (str,bytes)


class System():
	requiredWords = ["dia", "mass", "rad"]
	reservedWords = requiredWords + ["color", "avg_dia", "vel"]
	def __init__(self, path):
		self._index = {}
		self._roots = []
		raw = json.loads(open(path, "r").read(), object_pairs_hook=OrderedDict)
		def walk(tree, parent):
			for key in tree:
				if key in System.reservedWords:
					continue
				if not self._checkSpec(key, tree[key]):
					continue
				dia = self._formatNumber(tree[key]["dia"])
				mass = self._formatNumber(tree[key]["mass"])
				rad = self._formatNumber(tree[key]["rad"])
				if "color" in tree[key]:
					color = self._evalExpr(tree[key]["color"])
				else:
					color = self._evalExpr("WHITE")
				if "vel" in tree[key]:
					vel = [0, self._evalExpr(tree[key]["vel"])+parent.Velocity[1]]
				elif parent:
					vel = [0, math.sqrt(G*(parent.Mass**2)/(rad*(mass + parent.Mass)))+parent.Velocity[1]]
				else:
					vel = [0,0]
				b = Body(key, parent, dia, mass, vel, rad, color)
				self._index[key] = b
				if not parent:
					self._roots.append(b)
				walk(tree[key], b)
		walk(raw, None)

	def _evalExpr(self, exp):
		if isinstance(exp, basestring):
			ns = NAMESPACE.copy()
			exec("val="+exp, ns)
			return ns["val"]
		return exp

	def _formatNumber(self, number):
		return np.array([self._evalExpr(number)], dtype = np.float64)

	def _checkSpec(self, name, tree):
		for req in System.requiredWords:
			if req not in tree:
				#raise NameError("Body "+name+" has no "+req+" field.")
				print("Error: Body "+name+" has no "+req+" field. This body will not be added to the system.")
				return False
		return True

	def __iter__(self):
		return iter(self._index.values())#_sysiter(self._index.iteritems())

	def __getitem__(self, index):
		return self._index[index]

	def getRoots(self):
		return self._roots



if __name__ == "__main__":
	print("Running system tests")
	sys = System(os.path.abspath('resources/systems/solar.json'))
	sun = sys.getRoots()[0]
	print("System root is", sun)
	print()
	print("System map:")
	print(sun.show())
	mars = sys["Mars"]
	print(mars, "has", len(mars.getChildren()), "children")
	print()
	print("Printing relationships:\n")
	for b in sys:
		i = str(b)
		print(i+"'s parent is "+ (str(b.getParent()) if b.Parent else "None"))
		print(i+"'s children are "+str(list(b.getChildren())))
		#print i+"'s velocity is "+str(b.velocity)

