from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restx import Api, fields, Resource


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app, title="Flask API", validate=True)


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product = db.Column(db.String)
    supplier = db.Column(db.String)
    expiration_date = db.Column(db.Date, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    history = db.relationship("BatchHistory", backref="batch", lazy=True)


class BatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batch.id"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class BatchSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Batch


class BatchHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BatchHistory


batch_schema = BatchSchema(many=True)
batch_history_schema = BatchHistorySchema(many=True)
single_batch_schema = BatchSchema()

batch_model = api.model(
    "Batch",
    {
        "product": fields.String(),
        "supplier": fields.String(),
        "expiration_date": fields.Date(),
        "is_deleted": fields.Boolean(),
        "quantity": fields.Integer(),
    },
)

batch_edit = api.model(
    "BatchEdit",
    {
        "add_quantity": fields.Integer(),
    },
)

batch_history_model = api.model(
    "BatchHistory",
    {
        "batch_id": fields.Integer(),
        "timestamp": fields.Date(),
        "quantity": fields.Integer(),
    },
)


@api.route("/get_all")
class GetData(Resource):
    def get(self):
        return jsonify(batch_schema.dump(Batch.query.filter_by(is_deleted=False).all()))


@api.route("/get/<int:batch_id>")
class GetData(Resource):
    def get(self, batch_id):
        return single_batch_schema.dump(Batch.query.get(batch_id))


@api.route("/get_overview")
class GetData(Resource):
    def get(self):
        data = {
            "fresh": len(
                Batch.query.filter(
                    Batch.expiration_date > datetime.today().date(),
                    Batch.is_deleted == False,
                    Batch.quantity != 0,
                ).all()
            ),
            "expiring today": len(
                Batch.query.filter(
                    Batch.expiration_date == datetime.today().date(),
                    Batch.is_deleted == False,
                    Batch.quantity != 0,
                ).all()
            ),
            "expired": len(
                Batch.query.filter(
                    Batch.expiration_date < datetime.today().date(),
                    Batch.is_deleted == False,
                    Batch.quantity != 0,
                ).all()
            ),
        }
        return jsonify(data)


@api.route("/get_history/<int:batch_id>")
class GetData(Resource):
    def get(self, batch_id):
        return jsonify(
            batch_history_schema.dump(
                BatchHistory.query.filter_by(batch_id=batch_id).all()
            )
        )


@api.route("/add")
class PostData(Resource):
    @api.expect(batch_model)
    def post(self):
        batch = Batch(
            product=request.json["product"],
            supplier=request.json["supplier"],
            expiration_date=datetime.strptime(
                request.json["expiration_date"], "%Y-%m-%d"
            ),
            quantity=request.json["quantity"],
        )
        batch_history = BatchHistory(
            timestamp=datetime.now(),
            quantity=batch.quantity,
        )
        batch.history.append(batch_history)
        db.session.add(batch)
        db.session.add(batch_history)
        db.session.commit()
        return {"message": "data added to database"}


@api.route("/edit/<int:batch_id>")
class PutData(Resource):
    @api.expect(batch_edit)
    def put(self, batch_id):
        batch = Batch.query.get(batch_id)
        batch.quantity += request.json["add_quantity"]
        batch_history = BatchHistory(
            timestamp=datetime.now(),
            quantity=batch.quantity,
        )
        batch.history.append(batch_history)
        db.session.add(batch_history)
        db.session.commit()
        return {"message": "data updated"}


@api.route("/delete/<int:batch_id>")
class DeleteData(Resource):
    def put(self, batch_id):
        batch = Batch.query.get(batch_id)
        batch.is_deleted = True
        db.session.commit()
        return {"message": "data deleted successfully"}


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
