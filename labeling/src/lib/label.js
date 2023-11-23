import mongoose from 'mongoose';

const SCHEMA = new mongoose.Schema(
    {
        recipeId: { type: Number, required: true, unique: true},
        ingredientArr: { type: [Number], default: []},
        mainArr: { type: [Number], default: []},
        condimentArr: { type: [Number], default: []},
        spiceArr: { type: [Number], default: []},
    },
    {
        timestamps: true,
    }
);

export default mongoose.model('Label', SCHEMA);
