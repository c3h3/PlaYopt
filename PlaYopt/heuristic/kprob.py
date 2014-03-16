'''
Created on Mar 17, 2014

@author: c3h3
'''

import itertools
import numpy as np


class KProblem(object):
    
    def __init__(self, data, C):
        self.data = data
        self.C = C
        
        self.data = self.data[self.data["w"] <= self.C]
        self.sol = self.data["ptr"] < 0
        self.worse_data = self.data["ptr"] < 0
        
    def localize_ptrs(self,x):
        return np.in1d(self.data["ptr"],x)
    
    
    @property
    def sol_01_array(self):
        return_array = np.zeros(self.sol.shape)
        return_array[self.sol] = 1
        return return_array
    
    
    @property
    def bag_data(self):
        return self.data[self.sol]
    
    
    @property
    def outside_data(self):
        return self.data[np.logical_not(self.sol)]
    
    
    @property
    def outside_without_data(self):
        return self.data[np.logical_not(self.sol) & np.logical_not(self.worse_data)]
    
    
    @property
    def reC(self):
        return self.C - self.data["w"][self.sol].sum()
    
    
    @property
    def solv(self):
        return self.data["v"][self.sol].sum()
        
    
    @property
    def could_reC_add_more_objects(self):
#         print "~~[in could_reC_add_more_objects]~~"
#         print "self.reC = ",self.reC
#         print "self.outside_data = ",self.outside_data
        
        if (self.reC > 0)&(len(self.outside_data) > 0):
            return self.reC >= np.min(self.outside_data["w"])
        else: 
            return False
        
    @property
    def could_add_more_objects(self):
#         print "~~[in could_add_more_objects]~~"
#         print "self.feasible_objects = ",self.feasible_objects
#         print "self.feasible_objects.shape = ",self.feasible_objects.shape
#         print "len(self.feasible_objects) = ",len(self.feasible_objects)
#         print "len(self.feasible_objects) > 0 = ",len(self.feasible_objects) > 0
#         print "self.could_reC_add_more_objects = ",self.could_reC_add_more_objects
        
        return self.could_reC_add_more_objects & (self.feasible_objects.shape[0] > 0)
    
    @property
    def feasible_objects(self):
        return self.outside_data[self.outside_data["w"] <= self.reC]
    
    
#     @property
#     def sol_01_array(self):
#         temp_sol = np.zeros(self.sol.shape)
#         temp_sol[self.sol] = 1
#         return temp_sol
    
    
    def add_max_density_object(self):
 
        if self.could_add_more_objects:
            max_density_ptr = self.feasible_objects["ptr"][self.feasible_objects["d"].argsort()[-1]]
            
            local_ptr = self.data["ptr"] == max_density_ptr
            self.sol[local_ptr] = True
            
            
    def solve_by_density_greedy(self):
        
        while self.could_add_more_objects:
            self.add_max_density_object()
        
#         self.try_to_reduce_reC()
#         self.try_to_increase_solv()
        
#         do_reduce_reC_loop = True
        
#         while do_reduce_reC_loop:
#             old_reC = self.reC
#             self.try_to_reduce_reC()
#             new_reC = self.reC
#             if old_reC - new_reC > 0:
#                 do_reduce_reC_loop = True
#             else:
#                 do_reduce_reC_loop = False
            
#         do_update_solv_loop = True
        
#         while do_update_solv_loop:
#             old_solv = self.solv
#             self.try_to_increase_solv()
#             new_solv = self.solv
#             if new_solv - old_solv > 0:
#                 do_update_solv_loop = True
#             else:
#                 do_update_solv_loop = False
                
            
        
            
    @property
    def real_bag_density(self): 
        if self.reC > 0:
            return self.bag_data["v"] / (self.bag_data["w"]+self.reC)
        else:
            return self.bag_data["d"]
    
    
    def try_to_increase_solv(self, max_combs_k=5, without_worse_data=True, max_loop=100):
        continue_loop = True
        
        loop_count=0
        
        while continue_loop:
            loop_count = loop_count + 1
            if len(self.bag_data) > 0:
                all_combs = reduce(lambda yy,zz:yy+zz,map(lambda kk: [xx for xx in itertools.combinations(self.bag_data["ptr"],kk) if len(xx)>0] ,range(max_combs_k+1)))
                
                try_results = map(lambda xx:self.try_to_move_out(move_out_ptrs=np.array([xx]),
                                                                 without_worse_data=without_worse_data), 
                                    all_combs)
                
                filtered_try_results = [xx for xx in try_results if xx != None]
                
                if len(filtered_try_results) > 0:
                    dt = np.dtype([('mo', object),('mi', object),('inc', float)])
                    filtered_try_results_array = np.array(filtered_try_results,dtype=dt)
                    max_inc_ptr = filtered_try_results_array["inc"].argsort()[-1]
                    change_args = filtered_try_results_array[max_inc_ptr]                    
                    self.change(move_out_ptrs=change_args['mo'], move_in_ptrs=change_args['mi'])
        
                    if loop_count<=max_loop:
                        continue_loop=True
                    else:
                        continue_loop=False
                            
                else:
                    print "NOT len(filtered_try_results) > 0"
                    continue_loop=False
            else:
                print "NOT len(self.bag_data) > 0"
                continue_loop=False
            
    
    def try_to_reduce_reC(self, max_combs_k=5, without_worse_data=True, max_loop=100):
        
        continue_loop = True
        
        loop_count=0
        
        while continue_loop:
            loop_count = loop_count + 1
        
            if self.reC > 0:
            
                if len(self.bag_data) > 0:
                    all_combs = reduce(lambda yy,zz:yy+zz,map(lambda kk: [xx for xx in itertools.combinations(self.bag_data["ptr"],kk) if len(xx)>0] ,range(max_combs_k+1)))
                
                    try_results = map(lambda xx:self.try_to_move_out(move_out_ptrs=np.array([xx]),
                                                                     without_worse_data=without_worse_data), 
                                      all_combs)
                
                    filtered_try_results = [xx for xx in try_results if xx != None]
                
                    if len(filtered_try_results) > 0:
                        dt = np.dtype([('mo', object),('mi', object),('inc', float)])
                        filtered_try_results_array = np.array(filtered_try_results,dtype=dt)
                        max_inc_ptr = filtered_try_results_array["inc"].argsort()[-1]
                
                        change_args = filtered_try_results_array[max_inc_ptr]
                        
                        old_reC = self.reC
            
                        self.change(move_out_ptrs=change_args['mo'], move_in_ptrs=change_args['mi'])
        
                        new_reC = self.reC
                        
                        diff_reC = old_reC - new_reC
                        
                        if (loop_count<=max_loop) & (diff_reC>0):
                            continue_loop=True
                        else:
                            continue_loop=False
                            
                    else:
                        print "NOT len(filtered_try_results) > 0"
                        continue_loop=False
                else:
                    print "NOT len(self.bag_data) > 0"
                    continue_loop=False
            else:
                print "reC = ",self.reC
                print "nothing to reduce"
                continue_loop=False
                                
    
    def try_to_move_out(self, move_out_ptrs, without_worse_data=True):
        
        local_move_out_ptrs = np.in1d(self.data["ptr"],move_out_ptrs)
        original_value = self.data["v"][local_move_out_ptrs].sum()
        original_ws = self.data["w"][local_move_out_ptrs].sum()
        if without_worse_data:
            change_prob = type(self)(data=self.outside_without_data,
                                       C=self.reC + original_ws)
        else:
            change_prob = type(self)(data=self.outside_data,
                                       C=self.reC + original_ws)
        
        change_prob.solve_by_density_greedy()
        
        if change_prob.solv > original_value:
            return move_out_ptrs, change_prob.bag_data["ptr"], change_prob.solv - original_value
        elif change_prob.solv == original_value: 
            if change_prob.bag_data["w"].sum() < original_ws:
                return move_out_ptrs, change_prob.bag_data["ptr"], change_prob.solv - original_value
        
    
    def change(self, move_out_ptrs, move_in_ptrs):
        
        local_move_out_ptrs = self.localize_ptrs(move_out_ptrs)
        local_move_in_ptrs = self.localize_ptrs(move_in_ptrs)
        
        self.sol[local_move_out_ptrs] = False
        self.worse_data[local_move_out_ptrs] = True
        self.sol[local_move_in_ptrs] = True
        
        
        
        
    
    
    


if __name__ == '__main__':
    pass