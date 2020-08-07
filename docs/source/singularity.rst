Running CORTADO
=====================================

Hosting
-------

The containerization of this application is maintained and hosted on Singularity Hub. To inspect build, click: |build-location|

Pull the most recent container by typing the command below into a linux terminal, (**NOTE: you do not have to do this every time before executing the container!**)

.. code-block::
  
  singularity pull shub://tjhendrickson/CORTADO


Singularity Usage
-----------------

 At any time you can look at usage by typing in a terminal:
 
 .. code-block::
 
  singularity run /path/to/CORTADO/container -h
 

 .. |build-location| image:: https://www.singularity-hub.org/static/img/hosted-singularity--hub-%23e32929.svg
    :alt: build location
    :scale: 100%
    :target: https://singularity-hub.org/collections/3125