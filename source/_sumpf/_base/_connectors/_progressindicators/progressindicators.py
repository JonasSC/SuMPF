# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2015 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from .progressindicator_base import ProgressIndicator
from ..outputconnectors import OutputConnector


class ProgressIndicator_All(ProgressIndicator):
    """
    A progress indicator that takes all methods of a processing chain into account
    for estimating the progress of a calculation.
    This is often not optimal, when the calculation effort is not equally distributed
    between the different method types. If for example the setters only save some
    variables, while the getters do all the calculations, the estimation of the
    progress will be very bad, because the setters contribute as much to the estimated
    progress as the getters.
    """
    def _Filter(self, connector):
        """
        @retval : always True, because all methods are taken into account.
        """
        return True



class ProgressIndicator_Outputs(ProgressIndicator):
    """
    A progress indicator that takes only getter methods into account for estimating
    the progress of a calculation.
    This provides a better estimation of the progress, if most of the calculations
    are done in the getter methods.
    """
    def _Filter(self, connector):
        """
        @retval : True for getter methods, False otherwise.
        """
        if isinstance(connector, OutputConnector):
            return True
        else:
            return False



class ProgressIndicator_OutputsAndNonObservedInputs(ProgressIndicator):
    """
    A progress indicator that takes only getter methods and setter methods that
    do not affect any getters into account for estimating the progress of a calculation.
    This should generally provide a good estimation of the progress, if most of
    the calculations are done in the getter methods. If a setter method does not
    affect any getter methods, it is assumed, that this setter method also does
    an expensive calculation rather than just setting a value. This is often the
    case for "end point classes" in a processing chain like plotting classes.
    """
    def _Filter(self, connector):
        """
        @retval : True for getter methods and setters that do not affect any getters, False otherwise.
        """
        if isinstance(connector, OutputConnector):
            return True
        elif len(connector.GetObservers()) == 0:
            return True
        else:
            return False

