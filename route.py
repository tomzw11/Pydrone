import matplotlib.pyplot as plt 
import matplotlib.patches as patches

def route(root):

	root_height = root[2]

	coordinates = [\
[0.42*root_height+root[0],0.42*root_height+root[1],root_height/2],\
[-0.42*root_height+root[0],0.42*root_height+root[1],root_height/2],\
[-0.42*root_height+root[0],-0.15*root_height+root[1],root_height/2],\
[0.42*root_height+root[0],-0.15*root_height+root[1],root_height/2]]

	return coordinates

if __name__ == "__main__":

	meter_to_feet = 3.28
	root = [0,0,16*1]
	print 'root',root,'\n'

	level1 = route(root)
	print 'level 1 \n'
	print level1[0],'\n'
	print level1[1],'\n'
	print level1[2],'\n'
	print level1[3],'\n'

	print 'level 2 \n'
	level2 = [[0]*3]*4

	for x in xrange(4):
		level2[x] = route(level1[x])
		for y in xrange(4):
			print 'level2 point[',x+1,y+1,']',level2[x][y],'\n'

	fig, ax = plt.subplots()

	ball, = plt.plot(6.72+1.52,6.72+1.52,'mo')

	plt.plot(0,0,'bo')
	plt.plot([level1[0][0],level1[1][0],level1[2][0],level1[3][0]],[level1[0][1],level1[1][1],level1[2][1],level1[3][1]],'ro')

	rect_blue = patches.Rectangle((-13.44,-4.8),13.44*2,9.12*2,linewidth=1,edgecolor='b',facecolor='b',alpha = 0.1)
	ax.add_patch(rect_blue)

	rect_red = patches.Rectangle((0,4.23),13.44,9.12,linewidth=1,edgecolor='r',facecolor='r',alpha = 0.3)
	ax.add_patch(rect_red)

	plt.plot([level2[0][0][0],level2[0][1][0],level2[0][2][0],level2[0][3][0]],[level2[0][0][1],level2[0][1][1],level2[0][2][1],level2[0][3][1]],'go')

	rect_green = patches.Rectangle((6.72,6.72+4.23/2),13.44/2,9.12/2,linewidth=1,edgecolor='g',facecolor='g',alpha = 0.5)
	ax.add_patch(rect_green)

	linear_s = [12,12]
	plt.plot(12,12,'yo')
	rect_yellow = patches.Rectangle((10,11),13.44/4,9.12/4,linewidth=1,edgecolor='y',facecolor='y',alpha = 0.5)
	ax.add_patch(rect_yellow)

	ax.legend([ball,rect_blue,rect_red,rect_green,rect_yellow],['Ball','Root View','Level 1 - 4 anchors','Level 2 - 16 anchors','Linear Search - 64 anchors'])

	plt.axis([-13.44, 13.44, -4.8, 13.44])
	plt.show()









