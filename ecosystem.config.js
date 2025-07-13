module.exports = {
    apps: [{
        name: 'rnaseq-backend',
        script: 'gunicorn',
        args: '-c gunicorn.conf.py app:app',
        cwd: process.env.HOME + '/RNAseq_web',
        interpreter: 'none',
        env: {
            FLASK_ENV: 'production',
            PATH: process.env.HOME + '/RNAseq_web/.venv/bin:' + process.env.PATH
        }
    }]
}
