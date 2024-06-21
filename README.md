Elevator assignment code

The elevators at my apartment irritated me. The current procedure is, when you get to a floor, you select the floor you want to go to, then the system assigns an elevator car to you, which is problematic because:
1. Even if you come early, if your assigned elevator delays, then you're stuck.
2. The elavators can be delayed for any reason.
3. People who come after you can get an elevator before you do.

As a programmer, I thought to myself: "How can I improve this process if I had the power to do so?" I came up with a different approach.
1. Take floor input from a user i.e. {User floor:[user_destination, user_direction]}.
2. Maintain a state of the elevators and ensure that a user is assigned an elevator car which minimizes their wait time. 
3. Display the current floors the elevator is servicing always.

The idea is this code should be able to minimize wait time for all elevator requesting users, instead of assigning based on which elevator moved first or where it is at time of request.
