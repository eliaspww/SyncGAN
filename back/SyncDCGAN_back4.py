import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os
import random
import math
import scipy.ndimage.interpolation

#==================== Draw Figure ====================
def plot(samples, size):
    fig = plt.figure(figsize=size)
    gs = gridspec.GridSpec(size[0], size[1])
    gs.update(wspace=0.05, hspace=0.05)

    for i, sample in enumerate(samples):
        ax = plt.subplot(gs[i])
        plt.axis('off')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        plt.imshow(sample.reshape(28, 28), cmap='Greys_r')

    return fig

def plot_x(id, type, samp, size=(4,4)):
    fig = plot(samp, size)
    plt.savefig('out/{}_{}.png'.format(str(id).zfill(4), type), bbox_inches='tight')
    plt.close(fig)

def samp_fig(sess, size):
	x_samp = np.zeros([size[0], size[1], 784], dtype=np.float32)

	for i in range(int(size[0]/2)):
		z1_batch = sample_z(size[1], z1_dim)
		z2_batch = sample_z(size[1], z2_dim)
		c_batch = sample_z(size[1], c_dim)
		
		x_samp[i*2] = sess.run(G1_sample, feed_dict={z1_: z1_batch, c1_: c_batch})
		x_samp[i*2+1] = sess.run(G2_sample, feed_dict={z2_: z2_batch, c2_: c_batch})

	x_samp = x_samp.reshape(size[0]*size[1], 784)
	return x_samp

#==================== Data Batch ====================
def class_list(imgs, labels, c=10):
	imgs_class_list = []
	for i in range(c):
		imgs_class_list.append([])
	
	for i in range(labels.shape[0]):
		imgs_class_list[labels[i]].append(imgs[i])

	return np.asarray(imgs_class_list)

def next_batch(imgs, size):
    img_samp = np.ndarray(shape=(size, imgs.shape[1]))
    for i in range(size):
        r = random.randint(0,imgs.shape[0]-1)
        img_samp[i] = imgs[r]
    return img_samp

def sync_next_batch(img1_list, img2_list, size):
	img1_samp = []
	img2_samp = []

	for i in range(size):
		n = random.randint(0, len(img1_list)-1)
		r1 = random.randint(0, len(img1_list[n])-1)
		r2 = random.randint(0, len(img2_list[n])-1)

		img1_samp.append(img1_list[n][r1])
		img2_samp.append(img2_list[n][r2])

	img1_samp_np = np.asarray(img1_samp)
	img2_samp_np = np.asarray(img2_samp)
	sync_samp_np = np.ones((size, 1))

	return img1_samp_np, img2_samp_np, sync_samp_np

def nsync_next_batch(img1_list, img2_list, size):
	img1_samp = []
	img2_samp = []
	
	for i in range(size):
		n1 = random.randint(0, len(img1_list)-1)
		n2 = random.randint(0, len(img2_list)-1)
		while n1 == n2:
			n1 = random.randint(0, len(img1_list)-1)
			n2 = random.randint(0, len(img2_list)-1)			

		r1 = random.randint(0, len(img1_list[n1])-1)
		r2 = random.randint(0, len(img2_list[n2])-1)

		img1_samp.append(img1_list[n1][r1])
		img2_samp.append(img2_list[n2][r2])

	img1_samp_np = np.asarray(img1_samp)
	img2_samp_np = np.asarray(img2_samp)
	sync_samp_np = np.zeros((size, 1))

	return img1_samp_np, img2_samp_np, sync_samp_np

def sync_match_next_batch(img1_list, img2_list, size, cut=2000):
	img1_samp = []
	img2_samp = []

	for i in range(size):
		n = random.randint(0, len(img1_list)-1)
		r = random.randint(0, cut)

		img1_samp.append(img1_list[n][r])
		img2_samp.append(img2_list[n][r])

	img1_samp_np = np.asarray(img1_samp)
	img2_samp_np = np.asarray(img2_samp)
	sync_samp_np = np.ones((size, 1))

	return img1_samp_np, img2_samp_np, sync_samp_np

def nsync_match_next_batch(img1_list, img2_list, size):
	img1_samp = []
	img2_samp = []
	
	for i in range(size):
		n1 = random.randint(0, len(img1_list)-1)
		n2 = random.randint(0, len(img2_list)-1)

		r1 = random.randint(0, len(img1_list[n1])-1)
		r2 = random.randint(0, len(img2_list[n2])-1)

		img1_samp.append(img1_list[n1][r1])
		img2_samp.append(img2_list[n2][r2])

	img1_samp_np = np.asarray(img1_samp)
	img2_samp_np = np.asarray(img2_samp)
	sync_samp_np = np.zeros((size, 1))

	return img1_samp_np, img2_samp_np, sync_samp_np

def sample_z(m, n, type=1):
    if type == 0:
    	return np.random.uniform(-1., 1., size=[m, n])
    else:
    	return np.random.normal(0., 1., size=[m, n])


def CompareFig(sess, x1_train, x2_train, z1_dim, z2_dim, c_dim):
	x_fig = np.zeros([64, 784], dtype=np.float32)

	#Random sample
	c_samp = sample_z(8, c_dim)
	z1_samp = sample_z(8, z1_dim)
	z2_samp = sample_z(8, z2_dim)
	x_fig[0:8] = sess.run(G1_sample, feed_dict={z1_: z1_samp, c1_: c_samp})
	x_fig[8:16] = sess.run(G2_sample, feed_dict={z2_: z2_samp, c2_: c_samp})

	#Encode Latent
	x1_sync, x2_sync, _ = sync_match_next_batch(x1_train, x2_train, 8, cut=200)
	z1_re, c1_re = LatentEncode(sess, x1_sync, Info_grad1)
	z2_re, c2_re = LatentEncode(sess, x2_sync, Info_grad2)

	#Reconstruct
	z1_samp = sample_z(4, z1_dim)
	x1_re = sess.run(G1_sample, feed_dict={z1_:z1_re[0:4], c1_:c1_re[0:4]})
	x1_re_diff = sess.run(G1_sample, feed_dict={z1_:z1_samp, c1_:c1_re[4:8]})
	x21_re = sess.run(G1_sample, feed_dict={z1_:z1_re[0:4], c1_:c2_re[0:4]})
	x21_re_diff = sess.run(G1_sample, feed_dict={z1_:z1_samp, c1_:c2_re[4:8]})

	z2_samp = sample_z(4, z2_dim)
	x2_re = sess.run(G2_sample, feed_dict={z2_:z2_re[0:4], c2_:c2_re[0:4]})
	x2_re_diff = sess.run(G2_sample, feed_dict={z2_:z2_samp, c2_:c2_re[4:8]})
	x12_re = sess.run(G2_sample, feed_dict={z2_:z2_re[0:4], c2_:c1_re[0:4]})
	x12_re_diff = sess.run(G2_sample, feed_dict={z2_:z2_samp, c2_:c1_re[4:8]})

	#Fill data
	x_fig[16:24] = x1_sync
	x_fig[24:28] = x1_re
	x_fig[28:32] = x1_re_diff
	x_fig[32:36] = x21_re
	x_fig[36:40] = x21_re_diff

	x_fig[40:48] = x2_sync
	x_fig[48:52] = x2_re
	x_fig[52:56] = x2_re_diff
	x_fig[56:60] = x12_re
	x_fig[60:64] = x12_re_diff

	return x_fig

#==================== Parameter ====================
batch_size = 64
z1_dim = 8
z2_dim = 8
c_dim = 56

def xavier_init(size):
    if len(size) == 4:
        n_inputs = size[0]*size[1]*size[2]
        n_outputs = size[3]
    else:
        n_inputs = size[0]
        n_outputs = size[1]
    
    stddev = math.sqrt(3.0 / (n_inputs + n_outputs))
    return tf.truncated_normal(size, stddev=stddev)

def conv2d(x, W, stride):
    return tf.nn.conv2d(x ,W ,strides=stride, padding='SAME')

def deconv2d(x, W, output_shape, stride=[1,2,2,1]):
    return tf.nn.conv2d_transpose(x, W, output_shape, strides=stride, padding='SAME')

#==================== Placeholder ====================
z1_ = tf.placeholder(tf.float32, shape=[None, z1_dim])
z2_ = tf.placeholder(tf.float32, shape=[None, z2_dim])

c1_ = tf.placeholder(tf.float32, shape=[None, c_dim])
c2_ = tf.placeholder(tf.float32, shape=[None, c_dim])

x1_ = tf.placeholder(tf.float32, shape=[None, 784])
x2_ = tf.placeholder(tf.float32, shape=[None, 784])

s_ = tf.placeholder(tf.float32, shape=[None, 1])

#==================== Generator ====================
#Generator 1
W_m1_g_fc1 = tf.Variable(xavier_init([z1_dim+c_dim,7*7*128]))
b_m1_g_fc1 = tf.Variable(tf.zeros(shape=[7*7*128]))

W_m1_g_conv2 = tf.Variable(xavier_init([3,3,64,128]))
b_m1_g_conv2 = tf.Variable(tf.zeros(shape=[64]))

W_m1_g_conv3 = tf.Variable(xavier_init([5,5,1,64]))
b_m1_g_conv3 = tf.Variable(tf.zeros(shape=[1]))

var_g1 = [W_m1_g_fc1, b_m1_g_fc1, W_m1_g_conv2, b_m1_g_conv2, W_m1_g_conv3, b_m1_g_conv3]

def Generator1(z, c):
    z_c = tf.concat(axis=1, values=[z, c])
    h_g_fc1 = tf.nn.relu(tf.matmul(z_c, W_m1_g_fc1) + b_m1_g_fc1)
    h_g_re1 = tf.reshape(h_g_fc1, [-1, 7, 7, 128])

    output_shape_g2 = tf.stack([tf.shape(z)[0], 14, 14, 64])
    h_g_conv2 = tf.nn.relu(deconv2d(h_g_re1, W_m1_g_conv2, output_shape_g2) + b_m1_g_conv2)

    output_shape_g3 = tf.stack([tf.shape(z)[0], 28, 28, 1])
    h_g_conv3 = tf.nn.sigmoid(deconv2d(h_g_conv2, W_m1_g_conv3, output_shape_g3) + b_m1_g_conv3)

    h_g_re3 = tf.reshape(h_g_conv3, [-1,784])
    return h_g_re3

#Generator 2
W_m2_g_fc1 = tf.Variable(xavier_init([z2_dim+c_dim,7*7*128]))
b_m2_g_fc1 = tf.Variable(tf.zeros(shape=[7*7*128]))

W_m2_g_conv2 = tf.Variable(xavier_init([3,3,64,128]))
b_m2_g_conv2 = tf.Variable(tf.zeros(shape=[64]))

W_m2_g_conv3 = tf.Variable(xavier_init([5,5,1,64]))
b_m2_g_conv3 = tf.Variable(tf.zeros(shape=[1]))

var_g2 = [W_m2_g_fc1, b_m2_g_fc1, W_m2_g_conv2, b_m2_g_conv2, W_m2_g_conv3, b_m2_g_conv3]

def Generator2(z, c):
    z_c = tf.concat(axis=1, values=[z, c])
    h_g_fc1 = tf.nn.relu(tf.matmul(z_c, W_m2_g_fc1) + b_m2_g_fc1)
    h_g_re1 = tf.reshape(h_g_fc1, [-1, 7, 7, 128])

    output_shape_g2 = tf.stack([tf.shape(z)[0], 14, 14, 64])
    h_g_conv2 = tf.nn.relu(deconv2d(h_g_re1, W_m2_g_conv2, output_shape_g2) + b_m2_g_conv2)

    output_shape_g3 = tf.stack([tf.shape(z)[0], 28, 28, 1])
    h_g_conv3 = tf.nn.sigmoid(deconv2d(h_g_conv2, W_m2_g_conv3, output_shape_g3) + b_m2_g_conv3)

    h_g_re3 = tf.reshape(h_g_conv3, [-1,784])
    return h_g_re3

#==================== Discriminator ====================
#Discriminator 1
W_m1_d_conv1 = tf.Variable(xavier_init([5,5,1,4]))
b_m1_d_conv1 = tf.Variable(tf.zeros(shape=[4]))

W_m1_d_conv2 = tf.Variable(xavier_init([3,3,4,8]))
b_m1_d_conv2 = tf.Variable(tf.zeros(shape=[8]))

W_m1_d_fc3 = tf.Variable(xavier_init([7*7*8, 64]))
b_m1_d_fc3 = tf.Variable(tf.zeros(shape=[64]))

W_m1_d_fc4 = tf.Variable(xavier_init([64, 1]))
b_m1_d_fc4 = tf.Variable(tf.zeros(shape=[1]))

var_d1 = [W_m1_d_conv1, b_m1_d_conv1, W_m1_d_conv2, b_m1_d_conv2, W_m1_d_fc3, b_m1_d_fc3, W_m1_d_fc4, b_m1_d_fc4]

def Discriminator1(x):
	x_re = tf.reshape(x, [-1,28,28,1])
	h_d_conv1 = tf.nn.relu(conv2d(x_re, W_m1_d_conv1, [1,2,2,1]) + b_m1_d_conv1)

	h_d_conv2 = tf.nn.relu(conv2d(h_d_conv1, W_m1_d_conv2, [1,2,2,1]) + b_m1_d_conv2)
	h_d_re2 = tf.reshape(h_d_conv2, [-1,7*7*8])

	h_d_fc3 = tf.nn.relu(tf.matmul(h_d_re2, W_m1_d_fc3) + b_m1_d_fc3)
	
	y_logit = tf.matmul(h_d_fc3, W_m1_d_fc4) + b_m1_d_fc4
	y_prob = tf.nn.sigmoid(y_logit)
	
	return y_logit, y_prob

#Discriminator 2
W_m2_d_conv1 = tf.Variable(xavier_init([5,5,1,4]))
b_m2_d_conv1 = tf.Variable(tf.zeros(shape=[4]))

W_m2_d_conv2 = tf.Variable(xavier_init([3,3,4,8]))
b_m2_d_conv2 = tf.Variable(tf.zeros(shape=[8]))

W_m2_d_fc3 = tf.Variable(xavier_init([7*7*8, 128]))
b_m2_d_fc3 = tf.Variable(tf.zeros(shape=[128]))

W_m2_d_fc4 = tf.Variable(xavier_init([128, 1]))
b_m2_d_fc4 = tf.Variable(tf.zeros(shape=[1]))

var_d2 = [W_m2_d_conv1, b_m2_d_conv1, W_m2_d_conv2, b_m2_d_conv2, W_m2_d_fc3, b_m2_d_fc3, W_m2_d_fc4, b_m2_d_fc4]

def Discriminator2(x):
	x_re = tf.reshape(x, [-1,28,28,1])
	h_d_conv1 = tf.nn.relu(conv2d(x_re, W_m2_d_conv1, [1,2,2,1]) + b_m2_d_conv1)

	h_d_conv2 = tf.nn.relu(conv2d(h_d_conv1, W_m2_d_conv2, [1,2,2,1]) + b_m2_d_conv2)
	h_d_re2 = tf.reshape(h_d_conv2, [-1,7*7*8])

	h_d_fc3 = tf.nn.relu(tf.matmul(h_d_re2, W_m2_d_fc3) + b_m2_d_fc3)
	
	y_logit = tf.matmul(h_d_fc3, W_m2_d_fc4) + b_m2_d_fc4
	y_prob = tf.nn.sigmoid(y_logit)
	
	return y_logit, y_prob 

#==================== Synchronizer ====================
W_m1_s1 = tf.Variable(xavier_init([784,256]))
b_m1_s1 = tf.Variable(tf.zeros(shape=[256]))
W_m2_s1 = tf.Variable(xavier_init([784,256]))
b_m2_s1 = tf.Variable(tf.zeros(shape=[256]))

W_s_s2 = tf.Variable(xavier_init([512,256]))
b_s_s2 = tf.Variable(tf.zeros(shape=[256]))

W_s_s3 = tf.Variable(xavier_init([256,1]))
b_s_s3 = tf.Variable(tf.zeros(shape=[1]))

var_s = [ W_m1_s1, b_m1_s1, 
		  W_m2_s1, b_m2_s1,
		  W_s_s2, b_s_s2,
		  W_s_s3, b_s_s3 ]

def Synchronizer(x1, x2):
	h_m1_s1 = tf.nn.relu(tf.matmul(x1, W_m1_s1) + b_m1_s1)
	h_m2_s1 = tf.nn.relu(tf.matmul(x2, W_m2_s1) + b_m2_s1)

	h_concat_s1 = tf.concat(axis=1, values=[h_m1_s1, h_m2_s1])
	h_s2 = tf.nn.relu(tf.matmul(h_concat_s1, W_s_s2) + b_s_s2)
	y_s_logit = tf.matmul(h_s2, W_s_s3) + b_s_s3
	y_s_prob = tf.nn.sigmoid(y_s_logit)
	return y_s_logit, y_s_prob

#==================== Node Connect ====================
G1_sample = Generator1(z1_, c1_)
G2_sample = Generator2(z2_, c2_)

D1_real_logit, D1_real_prob = Discriminator1(x1_)
D1_fake_logit, D1_fake_prob = Discriminator1(G1_sample)

D2_real_logit, D2_real_prob = Discriminator2(x2_)
D2_fake_logit, D2_fake_prob = Discriminator2(G2_sample)

S_real_logit, S_real_prob = Synchronizer(x1_, x2_)
S_fake_logit, S_fake_prob = Synchronizer(G1_sample, G2_sample)

#==================== Loss & Train ====================
#Vanilla GAN Loss
D1_loss_real = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D1_real_logit, labels=tf.ones_like(D1_real_logit)))
D1_loss_fake = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D1_fake_logit, labels=tf.zeros_like(D1_fake_logit)))
D2_loss_real = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D2_real_logit, labels=tf.ones_like(D2_real_logit)))
D2_loss_fake = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D2_fake_logit, labels=tf.zeros_like(D2_fake_logit)))
D1_loss = D1_loss_real + D1_loss_fake 
D2_loss = D2_loss_real + D2_loss_fake

G1_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D1_fake_logit, labels=tf.ones_like(D1_fake_logit)))
G2_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=D2_fake_logit, labels=tf.ones_like(D2_fake_logit)))
'''
#W-GAN Loss
eps = 1e-8
D1_loss = -tf.reduce_mean(tf.log(D1_real_prob + eps) + tf.log(1. - D1_fake_prob + eps))
D2_loss = -tf.reduce_mean(tf.log(D2_real_prob + eps) + tf.log(1. - D2_fake_prob + eps))

G1_loss = -tf.reduce_mean(tf.log(D1_fake_prob + eps))
G2_loss = -tf.reduce_mean(tf.log(D2_fake_prob + eps))
'''
#Synchronize Loss
Ss_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=S_real_logit, labels=s_))
Gs_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=S_fake_logit, labels=s_))

#Solver 
G1_solver = tf.train.AdamOptimizer().minimize(G1_loss, var_list=var_g1)
G2_solver = tf.train.AdamOptimizer().minimize(G2_loss, var_list=var_g2)

D1_solver = tf.train.AdamOptimizer().minimize(D1_loss, var_list=var_d1)
D2_solver = tf.train.AdamOptimizer().minimize(D2_loss, var_list=var_d2)

Ss_solver = tf.train.AdamOptimizer().minimize(Ss_loss, var_list=var_s)
Gs_solver = tf.train.AdamOptimizer().minimize(Gs_loss, var_list=var_g1 + var_g2)

sess = tf.Session()
sess.run(tf.global_variables_initializer())

#Gradient Loss
Grad1_loss = tf.reduce_mean(tf.reduce_sum(tf.square(G1_sample - x1_), axis = 1))
Grad2_loss = tf.reduce_mean(tf.reduce_sum(tf.square(G2_sample - x2_), axis = 1))

C1_grad = tf.gradients(Grad1_loss, c1_)
Z1_grad = tf.gradients(Grad1_loss, z1_)
C2_grad = tf.gradients(Grad2_loss, c2_)
Z2_grad = tf.gradients(Grad2_loss, z2_)

Info_grad1 = {'C':c1_, 'Z':z1_, 'X':x1_, 'Cgrad':C1_grad, 'Zgrad':Z1_grad, 'Cdim':c_dim, 'Zdim':z1_dim}
Info_grad2 = {'C':c2_, 'Z':z2_, 'X':x2_, 'Cgrad':C2_grad, 'Zgrad':Z2_grad, 'Cdim':c_dim, 'Zdim':z2_dim}

def LatentEncode(sess, x, Info, rate=0.1, iter=1500):
    z = sample_z(x.shape[0], Info["Zdim"])
    c = sample_z(x.shape[0], Info["Cdim"])
    for i in range(iter):
        z_grad, c_grad = sess.run([Info["Zgrad"], Info["Cgrad"]], feed_dict={Info["Z"]:z, Info["C"]:c, Info["X"]:x})
        z_grad_np = np.asarray(z_grad[0])
        c_grad_np = np.asarray(c_grad[0])
        z -= rate * z_grad_np
        c -= rate * c_grad_np
    return z, c

#==================== Dataset ====================
mnist_digit = input_data.read_data_sets('MNIST_digit', one_hot=False)
x_digit_train = mnist_digit.train.images
y_digit_train = mnist_digit.train.labels
x_digit_test = mnist_digit.test.images
y_digit_test = mnist_digit.test.labels
x1_train = class_list(x_digit_train, y_digit_train, 10)
x1_test = class_list(x_digit_test, y_digit_test, 10)

mnist_fashion = input_data.read_data_sets('MNIST_fashion', one_hot=False)
x_fashion_train = mnist_fashion.train.images
y_fashion_train = mnist_fashion.train.labels
x_fashion_test = mnist_fashion.test.images
y_fashion_test = mnist_fashion.test.labels
x2_train = class_list(x_fashion_train, y_fashion_train, 10)
x2_test = class_list(x_fashion_test, y_fashion_test, 10)
'''
#Rotatate digit (cross domain)
x_digit_train_rot = scipy.ndimage.interpolation.rotate(x_digit_train.reshape(-1, 28, 28), 90, axes=(1, 2)).reshape(-1, 28*28)
x_digit_test_rot = scipy.ndimage.interpolation.rotate(x_digit_test.reshape(-1, 28, 28), 90, axes=(1, 2)).reshape(-1, 28*28)
x2_train = class_list(x_digit_train_rot, y_digit_train, 10)
x2_train = class_list(x_digit_train_rot, y_digit_test, 10)
'''
#==================== Main ====================
def Gaussian(x, sig):
	return np.exp(-x ** 2 /(2* sig **2))

def Dist(c1, c2):
	cr = c1 - c2
	d = np.zeros((cr.shape[0],1))
	for i in range(cr.shape[0]):
		d[i] = cr[i].dot(np.transpose(cr[i]))
	return d

if not os.path.exists('out/'):
    os.makedirs('out/')

i=0
for it in range(40001):
	#Get batch training data
	x1_sync, x2_sync, s_sync = sync_match_next_batch(x1_train, x2_train, batch_size)
	x1_nsync, x2_nsync, s_nsync = nsync_match_next_batch(x1_train, x2_train, batch_size)
	
	x1_batch = np.concatenate((x1_sync, x1_nsync), axis=0)
	x2_batch = np.concatenate((x2_sync, x2_nsync), axis=0)
	sr_batch = np.concatenate((s_sync, s_nsync), axis=0)

	z1_batch = sample_z(batch_size*2, z1_dim)
	z2_batch = sample_z(batch_size*2, z2_dim)

	c_sync_batch = sample_z(batch_size, c_dim)
	c1_nsync_batch = sample_z(batch_size, c_dim)
	c2_nsync_batch = sample_z(batch_size, c_dim)

	c1_batch = np.concatenate((c_sync_batch, c1_nsync_batch), axis=0)
	c2_batch = np.concatenate((c_sync_batch, c2_nsync_batch), axis=0)
	sf_batch = np.concatenate((np.ones((batch_size, 1)), np.zeros((batch_size, 1))), axis=0)
	#sf_batch = Gaussian(Dist(c1_batch, c2_batch), 64.)
	
	#Training
	_, loss_d1 = sess.run([D1_solver, D1_loss], feed_dict={z1_:z1_batch, c1_:c1_batch, x1_:x1_batch})
	_, loss_d2 = sess.run([D2_solver, D2_loss], feed_dict={z2_:z2_batch, c2_:c2_batch, x2_:x2_batch})
	_, loss_ss = sess.run([Ss_solver, Ss_loss], feed_dict={z1_:z1_batch, z2_:z2_batch, c1_:c1_batch, c2_:c2_batch, x1_:x1_batch, x2_:x2_batch, s_:sr_batch})

	_, loss_g1 = sess.run([G1_solver, G1_loss], feed_dict={z1_:z1_batch, c1_:c1_batch})
	_, loss_g2 = sess.run([G2_solver, G2_loss], feed_dict={z2_:z2_batch, c2_:c2_batch})
	_, loss_gs = sess.run([Gs_solver, Gs_loss], feed_dict={z1_:z1_batch, z2_:z2_batch, c1_:c1_batch, c2_:c2_batch, s_:sf_batch})
		
	#Show result
	if it%100 == 0:
		print("Iter: {}".format(it))
		print("  G1_loss: {:.4}, G2_loss: {:.4},".format(loss_g1, loss_g2))	
		print("  D1_loss: {:.4}, D2_loss: {:.4},".format(loss_d1, loss_d2))
		print("  Ss_loss: {:.4}, Gs_loss: {:.4}\n".format(loss_ss, loss_gs))
		
		x_samp = samp_fig(sess, (6,6))
		plot_x(i,'samp', x_samp, (6,6))
		i+=1

#Draw result figure
print("Save result figure ...")
size = (16,16)
x_samp = samp_fig(sess, size)
plot_x(0,'result', x_samp, size)

for i in range(4):
	x_fig = CompareFig(sess, x1_test, x2_test, z1_dim, z2_dim, c_dim)
	plot_x(0,'reconst_'+str(i), x_fig, (8,8))