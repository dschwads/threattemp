echo "Please make sure you've set your kubecfg to the appropriate cluster!"

if [ -z $(which kubectl) ] 
then
echo "please get kubectl";
exit 1;
else echo "attempting NodePort test";
echo "hope this is right:"
kubectl config get-contexts
echo -e "\nI am going to sleep for 5 seconds in case you need to ctrl-c and set the correct context."
sleep 5
fi

kubectl apply -f ./kubernetes/test/nginx-open.yaml
kubectl -n nginx-dbg get pods
kubectl scale -n nginx-dbg deployment nginx-dbg --replicas=0
kubectl delete -n nginx-dbg services nginx-dbg 
kubectl -n nginx-dbg get pods
