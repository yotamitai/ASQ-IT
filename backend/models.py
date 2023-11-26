from backend import db

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    free_txt = db.Column(db.String(100), nullable=False)
    start_state = db.Column(db.String(), nullable=False)
    end_state = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"Query('{self.start_state}', '{self.end_state}', '{self.free_txt}')"