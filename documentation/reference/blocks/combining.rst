Combining data sets
===================

This section documents classes, that combine multiple data sets into one.

.. autoclass:: sumpf.ConcatenateSignals

   .. automethod:: output()
   .. automethod:: add(signal)
   .. automethod:: remove(signal_id)
   .. automethod:: replace(signal_id, signal)


.. autoclass:: sumpf.MergeSignals

   .. autoattribute:: modes
   .. automethod:: output()
   .. automethod:: add(signal)
   .. automethod:: remove(signal_id)
   .. automethod:: replace(signal_id, signal)
   .. automethod:: set_mode(mode)


.. autoclass:: sumpf.MergeSpectrums

   .. autoattribute:: modes
   .. automethod:: output()
   .. automethod:: add(spectrum)
   .. automethod:: remove(spectrum_id)
   .. automethod:: replace(spectrum_id, spectrum)
   .. automethod:: set_mode(mode)
