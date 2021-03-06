import unittest
import numpy as np
from ocgis.exc import EmptySubsetError, ResolutionError
from ocgis.interface.base.dimension.base import VectorDimension


class TestVectorDimension(unittest.TestCase):
    
    def assertNumpyAll(self,arr1,arr2):
        return(self.assertTrue(np.all(arr1 == arr2)))
    
    def assertNumpyNotAll(self,arr1,arr2):
        return(self.assertFalse(np.all(arr1 == arr2)))
    
    def test_get_iter(self):
        vdim = VectorDimension(value=[10,20,30,40,50])
        with self.assertRaises(ValueError):
            list(vdim.get_iter())
            
        vdim = VectorDimension(value=[10,20,30,40,50],name='foo')
        tt = list(vdim.get_iter())
        self.assertEqual(tt[3],(3, {'foo_uid': 4, 'foo': 40, 'foo_bnds_lower': None, 'foo_bnds_upper': None}))
        
        vdim = VectorDimension(value=[10,20,30,40,50],bounds=[(ii-5,ii+5) for ii in [10,20,30,40,50]],name='foo',name_uid='hi')
        tt = list(vdim.get_iter())
        self.assertEqual(tt[3],(3, {'hi': 4, 'foo': 40, 'foo_bnds_lower': 35, 'foo_bnds_upper': 45}))
    
    def test_bad_keywords(self):
        with self.assertRaises(ValueError):
            VectorDimension(value=40,bounds=[38,42],dtype=float)
            
    def test_bad_dtypes(self):
        vd = VectorDimension(value=181.5,bounds=[181,182])
        self.assertEqual(vd.value.dtype,vd.bounds.dtype)
        
        with self.assertRaises(ValueError):
            VectorDimension(value=181.5,bounds=['a','b'])

    def test_one_value(self):
        values = [5,np.array([5])]
        for value in values:
            vdim = VectorDimension(value=value,src_idx=10)
            self.assertEqual(vdim.value[0],5)
            self.assertEqual(vdim.uid[0],1)
            self.assertEqual(len(vdim.uid),1)
            self.assertEqual(vdim.shape,(1,))
            self.assertNumpyAll(vdim.bounds,None)
            self.assertEqual(vdim[0].value[0],5)
            self.assertEqual(vdim[0].uid[0],1)
            self.assertEqual(vdim[0]._src_idx[0],10)
            self.assertNumpyAll(vdim[0].bounds,None)
            with self.assertRaises(ResolutionError):
                vdim.resolution
    
    def test_with_bounds(self):
        vdim = VectorDimension(value=[4,5,6],bounds=[[3,5],[4,6],[5,7]])
        self.assertNumpyAll(vdim.bounds,np.array([[3,5],[4,6],[5,7]]))
        self.assertNumpyAll(vdim.uid,np.array([1,2,3]))
        self.assertEqual(vdim.resolution,2.0)
    
    def test_boolean_slice(self):
        vdim = VectorDimension(value=[4,5,6],bounds=[[3,5],[4,6],[5,7]])
        vdim_slc = vdim[np.array([True,False,True])]
        self.assertFalse(len(vdim_slc) > 2)
        self.assertNumpyAll(vdim_slc.value,[4,6])
        self.assertNumpyAll(vdim_slc.bounds,[[3,5],[5,7]])
    
    def test_set_reference(self):
        vdim = VectorDimension(value=[4,5,6])
        vdim_slc = vdim[1]
        self.assertEqual(vdim_slc.uid[0],2)
        vdim_slc2 = vdim[:]
        self.assertNumpyAll(vdim_slc2.value,vdim.value)
        vdim._value[1] = 500
        self.assertNumpyAll(vdim.value,[4,500,6])
        with self.assertRaises(TypeError):
            vdim.bounds[1,:]
        self.assertNumpyAll(vdim.value,vdim_slc2.value)
        vdim_slc2._value[2] = 1000
        self.assertNumpyAll(vdim.value,vdim_slc2.value)
    
    def test_slice_source_idx_only(self):
        vdim = VectorDimension(src_idx=[4,5,6],data='foo')
        vdim_slice = vdim[0]
        self.assertEqual(vdim_slice._src_idx[0],4)
    
    def test_resolution_with_units(self):
        vdim = VectorDimension(value=[5,10,15],units='large')
        self.assertEqual(vdim.resolution,5.0)
    
    def test_load_from_source(self):
        vdim = VectorDimension(src_idx=[0,1,2,3],data='foo')
        self.assertNumpyAll(vdim.uid,np.array([1,2,3,4]))
        with self.assertRaises(NotImplementedError):
            vdim.value
        with self.assertRaises(NotImplementedError):
            vdim.resolution

    def test_empty(self):
        with self.assertRaises(ValueError):
            VectorDimension()
        
    def test_get_between(self):
        vdim = VectorDimension(value=[0])
        with self.assertRaises(EmptySubsetError):
            vdim.get_between(100,200)
        
        vdim = VectorDimension(value=[100,200,300,400])
        vdim_between = vdim.get_between(100,200)
        self.assertEqual(len(vdim_between),2)
    
    def test_get_between_bounds(self):
        vdim = VectorDimension(value=[0.,5.,10.],bounds=[[-2.5,2.5],[2.5,7.5],[7.5,12.5]])
        vdim_between = vdim.get_between(1,3)
        self.assertEqual(len(vdim_between),2)
        self.assertEqual(vdim.resolution,5.0)
        
        vdim_between = vdim.get_between(2.5,2.5)
        self.assertEqual(len(vdim_between),2)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()