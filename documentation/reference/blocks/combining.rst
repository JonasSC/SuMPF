Combining data sets
===================

This section documents classes, that combine multiple data sets into one.

.. autoclass:: sumpf.Concatenate

   .. automethod:: output()
   .. automethod:: add(data)
   .. automethod:: remove(data_id)
   .. automethod:: replace(data_id, data)


.. autoclass:: sumpf.Merge

   .. autoattribute:: modes
   .. automethod:: output()
   .. automethod:: add(data)
   .. automethod:: remove(data_id)
   .. automethod:: replace(data_id, data)
   .. automethod:: set_mode(mode)
