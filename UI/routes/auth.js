const express  =require('express');

const router = express.Router()

router.get('/login', (req, res) => {
	res.json({
		success: true,
		user: {
			username: 'test username'
		}
	})
})

module.exports = router