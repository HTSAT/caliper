## wuyanjun w00291783
## wu.wu@hisilicon.com
## Copyright @

import os
import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pylab import *
import numpy.numarray as na
import pdb
import radar_caliper as radar

PLOT_COLOR = ['ro-', 'yo-', 'bo-', 'go-', 'do-']

class DrawPicture:

    @staticmethod
    def draw_testpoint_picture( file_names, test_results, test_sub_items, folder ):
        """
        This function is used to draw the comparion histogram for the subItem

        :Param file_names: the input files which need to be compared
        :Param result_test: the test results in a Test Item, such as in 'performance' or 'functional'
        :Param test_sub_items: the Test Cases need to be draw, each Test Case means a picture
        :Param folder: the location will store the picture
        """
        #fig = figure(1, figsize=(3.25, 3))   
       
        # fig = matplotlib.pylot.gcf()
        # fig.set_size_inches(18.5, 10.5)
        #
        for subItem in test_sub_items:
            # get the Test Points in each Test SubItem
            test_point_dic = test_results[subItem]
            # get the keys of the Test Points, namely the Test Cases
            key_points = test_point_dic.keys()
            key_test_points = [x for x in key_points if x != 'Total_Scores']

            rcParams['figure.figsize'] = 9, 6
            # draw Test Points one by one
            for j in range(0, len(key_test_points)):
                # get the label of the Test Points in a Test Case
                label = test_point_dic[key_test_points[j]]['Point_Scores'].keys()
                # set the length of x axis
                x1 = na.array(range(len(label))) + 0.5
                fig, ax = plt.subplots()
                y_max = 0

                # draw the dot line for each file, namely, draw the target's content one by one
                for i in range(0, len(file_names)):
                    file_name = file_names[i]
                    fpi = open( file_name )
                    resultsi = yaml.load(fpi)
                    fpi.close()

                    try:
                        labeli = resultsi['name']
                        test_resultsi = resultsi['results']['Performance']
                        test_data = test_resultsi[subItem][key_test_points[j]]['Point_Scores']
                    except Exception, e:
                        print e
                        continue

                    #test_values = test_data.values()
                    test_values = []
                    for k in range(0, len(label)):
                        data = test_data[label[k]]
                        test_values.append( data )
                    y_value = max(test_values)
                    if (y_value > y_max):
                        y_max = y_value

                    try:
                        ax.plot(x1, test_values, PLOT_COLOR[i] , label=labeli)
                    except Exception, e:
                        print e
                        continue

                str_xlabel = 'Test Cases for ' + subItem + '_'  + key_test_points[j]
                title_name = key_test_points[j] + ' BarChart'
                ll = ax.legend(loc='upper right')
                leg = plt.gca().get_legend()
                ltext = leg.get_texts()
                plt.setp(ltext, fontsize='small')
                #rcParams.update({'legend.labelspacing':0.15})
                ax.set_xlabel(str_xlabel)
                ax.set_ylabel('Scores')
                ax.set_xticks(x1)
                ax.set_xticklabels(tuple(label))
                label_fig = ax.get_xticklabels()
                for label_tmp in label_fig:
                    label_tmp.set_rotation(30)
                    label_tmp.set_size('small')
                ax.set_title(title_name)
                plt.axis([0, len(label)*1.2, 0, y_max*1.05])
                plt.grid(True)
                png_name = os.path.join(folder,subItem + '_' + key_test_points[j] + '.png')
                plt.savefig( png_name, dit=150 )

    @staticmethod
    def draw_testSubItem_picture( file_names, test_subItems, folder ):
        items_Scores = []
        y_max = 0
        data_total = []
        label_total = []
        color_total = ['r', 'y', 'b', 'g', 'd']
        rects = []
        ind = 0
        width = 0.35
        rcParams['figure.figsize'] = 9, 6
        fig, ax = plt.subplots()   
       
        # get the lists of each Test SubItems from different targets
        for i in range(0, len(file_names)):
            fpi = open(file_names[i])
            results_i = yaml.load(fpi)
            fpi.close()
           
            try:
                label = results_i['name']
                label_total.append(label)
                test_resultsi = results_i['results']['Performance']
            except Exception:
                print e
                print "Error: %s"  % file_names[i]
                continue

            #calculate the total score of each subItems
            data = []

            for j in range(0, len(test_resultsi)):
                test_sub = test_resultsi[test_subItems[j]]
                data.append(test_sub['Total_Scores'])
       
                y_value = test_sub['Total_Scores']
                if(y_value > y_max):
                    y_max = y_value
            data_total.append(data)
        # compute the length of the x axis
        for i in range(0, len(label_total)):
            ind = na.array(range(len(test_resultsi)))+0.5
            width = 0.20
            rect_item = ax.bar(ind+i*width, data_total[i], width, color=color_total[i])
            rects.append(rect_item)

        ax.set_ylabel('Scores')
        ax.set_title('Total Score of each Items')
        ax.set_xticks(ind+width*len(rects)/2)
        ax.set_xticklabels( tuple(test_subItems) )
        #ax.xaxis_date()
        #ax.autoscale(tight=True)

        ax.legend(tuple(rects), tuple(label_total),  loc="upper left" )
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize='small')

        plt.ylim(0, y_max*1.08)
        # set the label for the labelling
        def autolabel(rectsi):
            for rect in rectsi:
                height = rect.get_height()
                ax.text(rect.get_x()+rect.get_width()/2., 1.02*height, '%.2f'%float(height),
                        ha='center', va='bottom')

        for i in range(0, len(rects)):
            autolabel(rects[i])
       
        png_name = os.path.join(folder, 'Total_Scores.png')

        plt.savefig( png_name, dit=512 )

def draw_radar(file_lists, store_folder):
    (spoke_labels, data_lists) = radar.get_Items_score(file_lists)
    dimension = len(spoke_labels)
    theta = radar.radar_factory(dimension, frame='circle')
    labels = [file_list.split('\/')[-1].split('_')[0] for file_list in file_lists]

    colors = ['b','r', 'g', 'm', 'y']
    if len(file_lists) < len(colors):
        colors = colors[0:len(file_lists)]
    title = 'Test Radar Diagram'

    fig = plt.figure(figsize=(9, 9))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    ax = fig.add_subplot(1, 1, 1, projection='radar')
    #for i in range(0, len(data_lists)):
    # get the approriate scale for the picture
    rgrid_list = get_rgrids(data_lists)

    #plt.rgrids( rgrid_list )
    ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1),
                horizontalalignment='center', verticalalignment='center')
    angles_list = [ th*180/np.pi for th in theta ]
    angles = np.array(angles_list)
    length = len(rgrid_list)
    data = radar.deal_data(data_lists)
   
    for d, color in zip(data, colors):
        ax.plot(theta, d, color=color)
        ax.fill(theta, d, facecolor=color, alpha=0.25)
  
    # FIXME: why can this work?
    #for angle, rgrid_data in zip(angles, rgrid_list):
    #    ax.set_rgrids(range(1, 1+length), angle=angle, labels=rgrid_data)
    ax.set_varlabels(spoke_labels)

    # the usage of subplot is plt.subplot(x, y, m)   m<=x*y
    plt.subplot(1, 1, 1)
    legend = plt.legend(labels, loc=(0.9, 0.95), labelspacing=0.1)
   
    plt.setp(legend.get_texts(), fontsize='small')
    plt.figtext(0.5, 0.965, 'Test of Drawing Radar Diagram for Caliper',
                ha='center', color='black', weight='bold', size='large')

    path_name = os.path.join(store_folder, "test.png")

    plt.savefig(path_name, dit=512)

def draw_picture(file_lists, picture_location):
    if len(file_lists) == 0:
        return

    fp = open( file_lists[0], "r" )
    results = yaml.load(fp)
    fp.close()
    """pdb.set_trace()"""
    # get Test SubItems in the 'Performance then draw the histogram for these subitems'
    test_results = results['results']['Performance']
    test_subItems = test_results.keys()
    DrawPicture.draw_testpoint_picture(file_lists, test_results, test_subItems, picture_location )
    DrawPicture.draw_testSubItem_picture( file_lists, test_subItems, picture_location )
    radar.draw_radar(file_lists, picture_location)


if __name__ == "__main__":
    file_lists = ['D01_16_result.yaml', 'D01_1_result.yaml', 'Server_result.yaml',
                    'TV_result.yaml']
    picture_location = "/home/wuyanjun/caliper/gen/output/html"
    try:
        radar.draw_radar(file_lists, picture_location)
    except Exception, e:
        raise e
 
    #draw_picture('')


