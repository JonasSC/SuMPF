Combining data sets
===================

This section documents classes, that combine multiple data sets into one.

.. autoclass:: sumpf.ConcatenateSignals

   .. automethod:: output()
   .. automethod:: add(signal)
   .. automethod:: remove(signal_id)
   .. automethod:: replace(signal_id, signal)


.. autoclass:: sumpf.MergeSignals

   .. automethod:: output()
   .. automethod:: add(signal)
   .. automethod:: remove(signal_id)
   .. automethod:: replace(signal_id, signal)
   .. automethod:: set_mode(mode)


.. autoclass:: sumpf.MergeSpectrums

   .. automethod:: output()
   .. automethod:: add(signal)
   .. automethod:: remove(signal_id)
   .. automethod:: replace(signal_id, signal)
   .. automethod:: set_mode(mode)
