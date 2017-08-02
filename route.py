def route(height,level):


	root_height = height

	level1 = [\
[0.42*root_height,0.15*root_height,root_height/2],\
[-0.42*root_height,0.15*root_height,root_height/2],\
[-0.42*root_height,-0.42*root_height,root_height/2],\
[0.42*root_height,-0.42*root_height,root_height/2]]

	return level1

if __name__ == "__main__":

	level1 = route(4,1)
	print level1






