Input/Output
============

This section documents classes, that interface *SuMPF* with the outside world.

.. autoclass:: sumpf.Jack

   .. automethod:: start(*args, **kwargs)
   .. automethod:: input(signal)
   .. automethod:: output()
   .. automethod:: sampling_rate()
   .. automethod:: input_ports()
   .. automethod:: add_input_port(short_name)
   .. automethod:: remove_input_port(port)
   .. automethod:: connect(output_port, input_port)
   .. automethod:: activate()
   .. automethod:: deactivate()
   .. automethod:: auto_deactivate(auto)
   .. automethod:: xruns()
