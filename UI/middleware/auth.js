exports.protect = (req, res, next) => {
  console.log(req)
  next()
}