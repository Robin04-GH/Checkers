class pieces():
    """
    Class containing the game pieces of both players as a reverse 
    dictionary : 
    - keys   = ID dark cells
    - values = ID 'man' [1..12]
    When a 'man' is promoted to a 'king', 12 is added to the ID.
    Player 1 has positive IDs, player 2 has negative IDs.
    """

    def __init__(self):
        """
        Constructor defines the reverse dictionary leaving it empty. 
        The loading of the pieces depends on whether a reset or a restore 
        from a configurable initial state is performed.

        @param -: .
        """

        self.pieces = {}

    # N.B.: with the exception you don't need to return a bool !
    def isValidCell(self, idDarkCell:int):
        if not (0 <= idDarkCell < 32):
            raise ValueError(f"Specified cell {idDarkCell} is out of bounds!")
        
    # N.B.: with the exception you don't need to return a bool !
    def isValidPiece(self, idPiece:int):
        if not (1 <= abs(idPiece) <= 24):
            raise ValueError(f"Invalid piece ID: {idPiece}. Useful interval abs[1..24] !")

    # N.B.: with the exception you don't need to return a bool !
    def isEmptyCell(self, idDarkCell:int):
        if idDarkCell not in self.pieces:
            raise KeyError(f"Cell {idDarkCell} empty !")

    # N.B.: with the exception you don't need to return a bool !
    def isNotEmptyCell(self, idDarkCell:int):
        if idDarkCell in self.pieces:
            raise KeyError(f"Cell {idDarkCell} already contains a piece !")

    def addPieces(self, idDarkCell:int, idPiece:int):
        self.isValidCell(idDarkCell)
        self.isValidPiece(idPiece)
        self.isNotEmptyCell(idDarkCell)

        self.pieces[idDarkCell] = idPiece

    def removePieces(self, idDarkCell:int):
        self.isValidCell(idDarkCell)
        self.isEmptyCell(idDarkCell)

        del self.pieces[idDarkCell]

    def updatePosition(self, originCell:int, targetCell:int):
        self.isValidCell(originCell)
        self.isValidCell(targetCell)

        # check for the presence of a piece on the original cell
        self.isEmptyCell(originCell)        
        # check for absence of a piece on the target cell
        self.isNotEmptyCell(targetCell)
        
        self.addPieces(targetCell, self.pieces[originCell])
        self.removePieces(originCell)

    def findIdPiece(self, idDarkCell:int)->int:
        self.isValidCell(idDarkCell)

        # if the cell contains no pieces it returns zero
        return self.pieces.get(idDarkCell, 0)
        
    def promotionKing(self, idDarkCell:int):
        # check for the presence of a piece on the specified cell
        self.isEmptyCell(idDarkCell)        

        idPiece = self.findIdPiece(idDarkCell)

        self.isValidPiece(idPiece)
        
        # promotion to King
        if 1 <= idPiece <= 12:
            idPiece += 12
        elif -1 >= idPiece >= -12:
            idPiece -= 12
        else:
            raise ValueError(f"The piece ID {idPiece} is already a king and cannot be promoted yet !")

        self.pieces[idDarkCell] = idPiece
