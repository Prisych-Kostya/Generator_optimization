# Generator in cafe time optimization project

#### A course project for “Operations and processes modeling” discipline (3-rd year, Applied mathematics faculty).

The purpose of the project is to calculate an electric generator optimal working periods during electricity outages for a cafe, to maximize profit.

Initial conditions (data):

- ***Electricity outages schedule***
- ***Clients arrival rates* for periods of time** (example: 8AM - {7, 6, 8, 8, 9, 8} (customers per every 10 minutes))
- ***Drinks profits and probabilities of ordering*** (example: cappuccino: 2$, 0.35 (35%))
- ***Generator fuel price***
- ***Generator minimal working time*** (minimal time that generator can work). It is needed to avoid non-realistic situations, where it is theoretically optimal to turn on ond off generator every 5-10 minutes.

Output data:

* Optimal time periods of generator working
* Estimated profit based on initial data
* Simulation of clients ordering drinks through the day with working generator in optimal time and factual profit
  (simulation is made using poisson distribution for time intervals between clients (using `numpy.generate_poiss_event()` func))
