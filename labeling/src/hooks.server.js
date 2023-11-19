import mongoose from 'mongoose'
import { MONGO_URI } from '$env/static/private'

mongoose.connect(MONGO_URI).then(() => {
    console.log('[MongoDB is connected]')
});
