# N-dimensional chess with dimensional collapse

## Introduction
Chess generalized to n dimensions (default board currently is just 3 dimensions)
rendered in 2D with the cubes along the 3rd dimension laid out next to each other in 2D (since chess fields are discrete, that works)

## Rules
### Pawn
- Moves 1 field along the dimension defined as forward
- Captures 1 field along the dimension defined as forward, then 1 field along any other dimension

### Knight
- Moves + Captures 2 fields along one dimension, then 1 field in another dimension
### Bishop
- Moves + Captures along a diagonal any number of steps
- A diagonal step is defined as 1 field along all dimensions
### Rook
- Moves + Captures along a straight line any number of steps
- A straight line step is defined as 1 field along exactly 1 dimension
side note: the rook is thus "more restricted" in higher dimensions than the bishop
### Queen
- Bishop + Rook moves
### King
- Moves + Captures 1 field in any non-zero number of directions
### Cannon
- Moves like a rook
- Captures by jumping over exactly 1 piece in a straight line, then capturing a piece after

## Board state
Let n = number of dimensions of the board.

The entire board is an array of fields of shape (w_1, ..., w_n).

Each field has a dimension in the interval [0, n].

A field with dimension 0 is essentially deleted, and counts as non-existent.

A field's dimension is defined by the number of standard basis directions (by only changing one coordinate), along which there are other fields of dimension not 0. 

A field always has a coordinate of shape (n,), regardless of which dimension it is.

---

e.g.:

a 2D field on a 3D board will have 3 coordinates (x_1, x_2, x_3)

The field is 2D because there is one dimension j, for which there exists a k, such that dimension of the field at (x_1, x_2, x_3) + k * e_j is 0.

## Research
Pawns are academic research pawns, and contribute to a player's level of research for the dimension of the field the pawns are in.

Once a player has reached a certain level of research along a dimension, all Cannons on fields of this dimension become armed, and any capture move they make will cause the dimension along their capture to collapse.

## Dimensional Collapse
Dimensional Collapse can only be initiated by a Cannon's capture move.

Thus each dimensional collapse is uniquely characterized by a dimension j, along which the cannon moved, and the values `start_j, stop_j`, of the field the cannon started on along that dimension, and the field the cannon landed on.

Let `start, stop` be the coordinates of the start and stop field of that cannon.

This capture move immediately deletes (sets dimension to 0) of all fields with `stop + k * e_j, k!=0`.

The field stop thus now has dimensionality `(old_dimension - 1)`.

The cannon is immediately removed from the game.

Then the majority owner of pieces on the fields that were removed will put the closest piece to the collapse site on coordinate `stop`.